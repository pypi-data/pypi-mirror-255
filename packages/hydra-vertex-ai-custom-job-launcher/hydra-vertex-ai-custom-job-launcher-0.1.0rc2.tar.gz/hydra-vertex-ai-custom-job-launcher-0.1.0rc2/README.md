# hydra-vertex-ai-custom-job-launcher

This repository aims to implement unofficially an Hydra Vertex AI Custom Job launcher, based on the template found here: https://github.com/facebookresearch/hydra/tree/main/examples/plugins/example_launcher_plugin.

While Custom Job can run any arbitrary code, they were designed to run ML training jobs on demand, and thus should be mainly considered for those tasks only.

A merge to the main branch of Hydra will be tempted.

**Note: This is an work in progress, and is subject to breaking changes**

## How to install/use

1. Install the plugin using `pip install ???`
2. Either define the launcher in your Hydra configuration group or override it in the defaults list of any config file such as:
```
# hydra/vertex_ai.yaml
hydra:
    launcher:
        _target_: hydra_plugins.vertex_ai_custom_job_launcher.custom_job_launcher.VertexAICustomJobLauncher
        # The configuration of the launcher
        ...

# hydra/vertex_ai.yaml
defaults:
- launcher: vertex_ai_custom_job

hydra:
    launcher:        
        # The configuration of the launcher
        ...

# example/config.yaml
defaults:
    - override hydra/launcher vertex_ai_custom_job

hydra:
    launcher:
        # The configuration of the launcher
        ...
```
3. Define the Custom Job configuration, as such (for a more thorough description of the arguments and their allowed values/triggered behaviors, see https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform#google_cloud_aiplatform_init and https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.CustomJob#google_cloud_aiplatform_CustomJob_from_local_script):
- `project_id`: GCP project ID (ex: `my-project-id`)
- `location`: GCP server location (ex: `us-central1`)
- `staging_bucket`: GCS storage bucket URL used for staging the jobs (ex: `gs://my-bucket`)
- `experiment`: Vertex AI experiment name, used for Vertex AI hosted grouped ML experiment tracking and logging. Can be null. (ex: `my-experiment`)
- `experiment_tensorboard`: Vertex AI Tensorboard. Can be a boolean or a Tensorboard resource name (ex: `projects/123/locations/us-central1/tensorboards/456`)
- `display_name`: Custom Job display name (ex: `my-custom-job`)
- `container_uri`: Container of the training image, either in the Artifact Registery, the Container Registery or Docker Hub. This includes as much prebuilt images provided publicly (ex: `python:3.10`) or by Vertex AI, or images built and pushed to the Artifact or Container registery (ex: `us-central1-docker.pkg.dev/my-project-id/my-task-name/my-image-name:latest`)
- `machine_type`: Machine type used to run the jobs. See https://cloud.google.com/vertex-ai/docs/training/configure-compute#machine-types for a list of accepted values.
- `accelerator_type`: GPU/TPU accelator used to run the jobs. See https://cloud.google.com/vertex-ai/docs/reference/rest/v1/MachineSpec for a list of accepted values.
- `accelerator_count`: Number of accelerator on the machine (>= 0)
- `boot_disk_type`: Type of disk used, either `pd-standard` for standard hard drive or `pd-ssd` for SSD.
- `boot_disk_size-gb`: Disk size in gigabytes.
- `base_ouput_dir`: GCS output directory of jobs.
- `service_account_email`: Service account email used for sumbitting the jobs. If Application-Default-Credentials are allowed and activated, the user mail can be directly used as service account email.

## TODO:
- Make 0.1 github release and adapt code to handle the public package
- Switch from the convenient CustomJob.from_local_script to a more custom approach using CustomJob and command lines, to avoid all the clutter made on the staging bucket by Vertex AI API backend
- Expand and stabilize the launcher configuration
- Look on all the AIP path that Vertex AI uses
- Add more control on job statuses and returns handling