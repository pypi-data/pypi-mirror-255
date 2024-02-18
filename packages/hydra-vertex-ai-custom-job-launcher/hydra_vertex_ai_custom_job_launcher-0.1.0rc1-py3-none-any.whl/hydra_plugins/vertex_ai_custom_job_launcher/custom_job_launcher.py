from __future__ import annotations
import logging
from typing import Optional, Sequence

from hydra.types import HydraContext
from hydra.core.singleton import Singleton
from hydra.core.utils import (
    JobReturn,
    configure_log,
    filter_overrides,
    setup_globals,
)
from hydra.plugins.launcher import Launcher
from hydra.types import TaskFunction
from omegaconf import DictConfig, open_dict, OmegaConf

from hydra_plugins.vertex_ai_custom_job_launcher import __version__

log = logging.getLogger(__name__)

def launch_custom_jobs(
    launcher: VertexAICustomJobLauncher,
    job_overrides: Sequence[Sequence[str]],
    initial_job_idx: int,
) -> Sequence[JobReturn]:
    """
    Launch as many custom jobs as there are job overrides.
    """

    # Lazy imports, to avoid slowing down the registration of all other plugins
    import glob
    import os
    import subprocess
    import sys
    import time
    import tempfile

    import cloudpickle
    import fsspec
    from google.cloud import aiplatform

    # Set up global Hydra variables
    setup_globals()

    # Assert that the launcher has been set up
    assert launcher.config is not None
    assert launcher.hydra_context is not None
    assert launcher.task_function is not None

    # Configure the logging subsystem
    configure_log(launcher.config.hydra.hydra_logging, 
                  launcher.config.hydra.verbose)
    log.info(f"Hydra logging configured with {launcher.config.hydra.hydra_logging} and verbose {launcher.config.hydra.verbose}.")

    # Set up variables to avoid cluttering the code
    project_id = launcher.init.project_id
    location = launcher.init.location
    staging_bucket = launcher.init.staging_bucket
    experiment = launcher.init.experiment
    experiment_tensorboard = launcher.init.experiment_tensorboard
    display_name = launcher.custom_job.display_name
    worker_pool_specs = launcher.custom_job.worker_pool_specs
    base_output_dir = launcher.custom_job.base_output_dir
    labels = launcher.custom_job.labels
    service_account_email = launcher.custom_job.service_account_email

    # Set up the filesystem for the staging bucket
    log.info(f"Setting up the filesystem for the staging bucket {staging_bucket}...")
    fs_url = fsspec.core.url_to_fs(staging_bucket)
    fs: fsspec.AbstractFileSystem = fs_url[0]

    # Set up Hydra sweep absolute paths
    sweep_output_gs_dir = os.path.join(staging_bucket, launcher.config.hydra.sweep.dir)
    sweep_output_gcs_dir = sweep_output_gs_dir.replace("gs://", "/gcs/")
    log.info(f"Setting up Hydra sweep absolute paths with:")
    log.info(f"- GS directory URL (used by launcher process): {sweep_output_gs_dir}")
    log.info(f"- GCS dir (used by Custom Job executing process): {sweep_output_gcs_dir}")
    launcher.config.hydra.sweep.dir = sweep_output_gcs_dir

    # Build the package in a temporary directory from the package root directory (2 level-up directory of this file)
    # and copy it to the Hydra job sweep GCS directory
    package_root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    with tempfile.TemporaryDirectory() as package_temp_dir:
        log.info(f"Building the package from {package_root_dir} to temporary directory {package_temp_dir}...")
        os.chdir(package_root_dir)
        result = subprocess.run([sys.executable, 'setup.py', 'sdist', '--dist-dir', package_temp_dir], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
        if result.returncode != 0:
            log.error(f"Build error: {result.stderr}")
            raise RuntimeError(f"Error building the package: {result.stderr}")
        package_dist_path = glob.glob(f"{package_temp_dir}/*.tar.gz")[0]
        log.info(f"Package built at {package_dist_path}.")
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        package_dist_gcs_path = os.path.join(sweep_output_gs_dir, "package_dist.tar.gz")
        fs.put(package_dist_path, package_dist_gcs_path)

    # Copy the job execution script to the GCS directory
    log.info(f"Copying the job execution script to the GCS directory {sweep_output_gs_dir}...")
    job_exec_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_custom_job_exec.py")
    job_exec_script_gcs_path = f"{sweep_output_gs_dir}/custom_job_exec.py"
    fs.put(job_exec_script_path, job_exec_script_gcs_path)

    # Set the copy commands, to copy the package distribution and job execution script from the GCS directory
    package_dist_copy_cmd = f"""cp {package_dist_gcs_path.replace("gs://", "/gcs/")} ."""
    log.info(f"Initializing package distribution copy command for all jobs with {package_dist_copy_cmd}...")
    custom_job_exec_script_copy_cmd = f"""cp {job_exec_script_gcs_path.replace("gs://", "/gcs/")} ."""
    log.info(f"Initializing custom job script copy command for all jobs with {custom_job_exec_script_copy_cmd}...")

    # Set the requirement installation command, to install the requirements from the package distribution
    custom_job_exec_install_cmd = "pip install package_dist.tar.gz"
    log.info(f"Initializing custom job requirements installation command for all jobs with {custom_job_exec_install_cmd}...")

    # Initialize Vertex AI
    log.info(f"Initializing Vertex AI with:")
    log.info(f"- Project: {project_id}")
    log.info(f"- Location: {location}")
    log.info(f"- Staging_bucket: {staging_bucket}")
    log.info(f"- Experiment: {experiment}")
    log.info(f"- Experiment_tensorboard: {experiment_tensorboard}")
    aiplatform.init(
        project=project_id,
        location=location,
        staging_bucket=staging_bucket,
        experiment=experiment,
        experiment_tensorboard=experiment_tensorboard
    )

    # For each job override:
    # - Load the sweep config and set the job id and job num.
    # - Pickle the job specs (hydra context, sweep config, task function and singleton state) into a temporary directory.
    # - Initialize the Vertex AI Custom Job, setting the container spec command to the task script and
    #   the container spec args to the temporary directory.
    # - Submit the job asynchronously.
    jobs: list[aiplatform.CustomJob] = []
    temp_dirs: list[str] = []
    log.info(f"Launching {len(job_overrides)} custom jobs on Vertex AI...")
    for idx, overrides in enumerate(job_overrides):

        # Set the job id from the initial job idx and the current idx
        idx = initial_job_idx + idx

        # Log the job id and overrides
        lst = " ".join(filter_overrides(overrides))
        log.info(f"- #{idx} : {lst}")

        # Load the sweep config and set the job num
        log.info(f"Loading sweep config for job #{idx}...")
        sweep_config = launcher.hydra_context.config_loader.load_sweep_config(
            launcher.config, list(overrides)
        )
        with open_dict(sweep_config):
            sweep_config.hydra.sweep.dir = sweep_output_gcs_dir
            sweep_config.hydra.job.num = idx

        # Initialize the Hydra GCS directory from :
        # - The staging bucket URL of the Vertex AI Custom Job
        # - The hydra sweep directory
        # - The hydra sweep subdir
        sweep_output_gs_subdir = os.path.join(
            sweep_output_gs_dir,
            sweep_config.hydra.sweep.subdir,
        )
        sweep_output_gcs_subdir = sweep_output_gs_subdir.replace("gs://", "/gcs/")
        log.info(f"Initializing Hydra GCS directory for job #{idx}...")
        log.info(f"- GS subdir URL: {sweep_output_gs_subdir}")
        log.info(f"- GCS subdir URL: {sweep_output_gcs_subdir}")
        temp_dirs.append(sweep_output_gs_subdir)
        fs.mkdir(sweep_output_gs_subdir)

        # Pickle the job specs, so that they can be passed to the custom job.
        log.info(f"Pickling job specs for job #{idx} to {sweep_output_gs_subdir}/job_specs.pkl...")
        job_specs = {
            "hydra_context": launcher.hydra_context,
            "sweep_config": sweep_config,
            "task_function": launcher.task_function,
            "singleton_state": Singleton.get_state(),
        }
        with fsspec.open(f"{sweep_output_gs_subdir}/job_specs.pkl", "wb") as f:
            cloudpickle.dump(job_specs, f)

        # Set the execution command, to install the requirements, copy and run the execution script
        custom_job_exec_script_path = f"custom_job_exec.py"
        custom_job_exec_cmd = f"""python {custom_job_exec_script_path} {sweep_output_gcs_subdir}"""
        log.info(f"Initializing custom job script execution command for job #{idx} with {custom_job_exec_cmd}...")
        copy_install_exec_cmd = (f"{package_dist_copy_cmd} && {custom_job_exec_script_copy_cmd} && " + 
                                 f"{custom_job_exec_install_cmd} && {custom_job_exec_cmd}")

        # Override the command of the worker pool spec to the execution command
        log.info(f"Overriding the command of the worker pool specs for job #{idx} with {copy_install_exec_cmd}...")
        for worker_pool_spec in worker_pool_specs:
            worker_pool_spec.container_spec.command = ["sh", "-c", copy_install_exec_cmd]
            worker_pool_spec.container_spec.args = []

        # Convert the worker pool specs to a list of dictionaries
        worker_pool_specs = OmegaConf.to_container(worker_pool_specs, resolve=True)

        # Initialize the custom job
        log.info(f"Initializing custom job #{idx} with:")
        log.info(f"- Display name: {display_name}")
        log.info(f"- Worker pool specs: {worker_pool_specs}")
        log.info(f"- Base output dir: {base_output_dir}")
        log.info(f"- Labels: {labels}")
        job = aiplatform.CustomJob(
            display_name=display_name,
            worker_pool_specs=worker_pool_specs,
            base_output_dir=base_output_dir,
            labels=labels
        )

        # Submit the job
        log.info(f"Submitting custom job #{idx} with service account {service_account_email}...")
        job.submit(service_account=service_account_email)
        
        # Append the job to the list of jobs
        jobs.append(job)

    # Wait for the jobs to complete
    log.info("Waiting for the jobs to complete...")
    for job in jobs:
        log.info(f"Waiting for job {job.name} to complete...")
        while job.state not in [aiplatform.gapic.JobState.JOB_STATE_SUCCEEDED,
                                aiplatform.gapic.JobState.JOB_STATE_FAILED,
                                aiplatform.gapic.JobState.JOB_STATE_CANCELLED]:
            time.sleep(1)
        log.info(f"Job {job.name} completed with state {job.state}.")

    # Read the job returns and delete the temporary directories
    log.info("Reading the job returns...")
    job_returns: list[JobReturn] = []
    for hydra_job_gcs_dir in temp_dirs:
        log.info(f"Reading the job return from {hydra_job_gcs_dir}/job_returns.pkl...")
        with fsspec.open(f"{hydra_job_gcs_dir}/job_returns.pkl", "rb") as f:
            job_return = cloudpickle.load(f)
        job_returns.append(job_return)

    # Return the job returns
    return job_returns

class VertexAICustomJobLauncher(Launcher):

    def __init__(
        self,
        **kwargs
    ) -> None:
        
        self.config: Optional[DictConfig] = None
        self.task_function: Optional[TaskFunction] = None
        self.hydra_context: Optional[HydraContext] = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    def setup(
        self,
        *,
        hydra_context: HydraContext,
        task_function: TaskFunction,
        config: DictConfig,
    ) -> None:
        self.config = config
        self.hydra_context = hydra_context
        self.task_function = task_function

    def launch(
        self, job_overrides: Sequence[Sequence[str]], initial_job_idx: int
    ) -> Sequence[JobReturn]:
        """
        :param job_overrides: a List of List<String>, where each inner list is the arguments for one job run.
        :param initial_job_idx: Initial job idx in batch.
        :return: an array of return values from run_job with indexes corresponding to the input list indexes.
        """
        return launch_custom_jobs(self, job_overrides, initial_job_idx)
