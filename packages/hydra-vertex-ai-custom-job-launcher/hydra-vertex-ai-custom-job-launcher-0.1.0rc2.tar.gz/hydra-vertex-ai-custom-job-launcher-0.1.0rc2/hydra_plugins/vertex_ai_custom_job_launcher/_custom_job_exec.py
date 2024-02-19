import logging
import sys

from hydra.core.singleton import Singleton
from hydra.core.utils import (
    run_job,
    setup_globals
)
from hydra.core.hydra_config import HydraConfig

log = logging.getLogger(__name__)

import fsspec
import cloudpickle

def custom_job_task(
    sweep_output_gcs_subdir: str
) -> None:
    """
    Load the job specs from the pickle file and run the Hydra job.
    """

    # Load the job specs from the pickle file
    log.info(f"Loading job specs from {sweep_output_gcs_subdir}/job_specs.pkl...")
    with fsspec.open(f"{sweep_output_gcs_subdir}/job_specs.pkl", "rb") as f:
        job_specs = cloudpickle.load(f)

    # Decompose the job specs into Hydra context, singleton state, sweep config, and task function
    hydra_context = job_specs["hydra_context"]
    singleton_state = job_specs["singleton_state"]
    sweep_config = job_specs["sweep_config"]
    task_function = job_specs["task_function"]

    # Set up global Hydra variables
    log.info(f"Setting up global Hydra variables...")
    setup_globals()

    # Set state for the Hydra singleton
    log.info(f"Setting state for the Hydra singleton...")
    Singleton.set_state(singleton_state)

    # Set up Hydra Config instance config
    log.info(f"Setting up Hydra Config instance config...")
    HydraConfig.instance().set_config(sweep_config)

    # Run the Hydra job
    log.info(f"Running the Hydra job...")
    job_return = run_job(
        hydra_context=hydra_context,
        config=sweep_config,
        task_function=task_function,
        job_dir_key="hydra.sweep.dir",
        job_subdir_key="hydra.sweep.subdir",
        configure_logging=True
    )

    # Pickle the job returns
    log.info(f"Pickling the job returns to {sweep_output_gcs_subdir}/job_returns.pkl...")
    with fsspec.open(f"{sweep_output_gcs_subdir}/job_returns.pkl", "wb") as f:
        cloudpickle.dump(job_return, f)

# Called by the Vertex AI custom job launcher
if __name__ == "__main__":
    custom_job_task(sys.argv[1])