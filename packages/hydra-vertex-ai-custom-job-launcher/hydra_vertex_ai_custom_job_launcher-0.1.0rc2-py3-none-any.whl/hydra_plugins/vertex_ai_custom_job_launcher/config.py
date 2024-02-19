# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
from dataclasses import dataclass, field
from typing import List, Dict, Union
from omegaconf import MISSING

from hydra.core.config_store import ConfigStore

@dataclass
class VertexAIInitConf:
    project_id: str = MISSING
    location: str = MISSING
    staging_bucket: str = MISSING
    experiment: str | None = None 
    experiment_tensorboard: Union[bool, str] = False

@dataclass
class MachineSpecConf:
    machine_type: str = "n1-standard-4"
    accelerator_count: int = 0
    accelerator_type: str = "ACCELERATOR_TYPE_UNSPECIFIED"

@dataclass
class ContainerSpecConf:
    image_uri: str = MISSING

@dataclass
class DiskSpecConf:
    boot_disk_type: str = "pd-ssd"
    boot_disk_size_gb: int = 100

@dataclass
class WorkerPoolSpecConf:
    container_spec: ContainerSpecConf = field(default_factory=ContainerSpecConf)
    machine_spec: MachineSpecConf = field(default_factory=MachineSpecConf)
    replica_count: int = 1
    disk_spec: DiskSpecConf = field(default_factory=DiskSpecConf)

@dataclass
class VertexAICustomJobConf:
    display_name: str = MISSING
    worker_pool_specs: List[Dict] = MISSING
    base_output_dir: str = MISSING
    labels: Dict[str, str] = field(default_factory=dict)
    service_account_email: str = MISSING
    
@dataclass
class VertexAICustomJobLauncherConf:
    init: VertexAIInitConf = field(default_factory=VertexAIInitConf)
    custom_job: VertexAICustomJobConf = field(default_factory=VertexAICustomJobConf)
    _target_: str = (
        "hydra_plugins.vertex_ai_custom_job_launcher.custom_job_launcher.VertexAICustomJobLauncher"
    )

ConfigStore.instance().store(
    group="hydra/launcher",
    name="vertex_ai_custom_job",
    node=VertexAICustomJobLauncherConf,
    provider="vertex_ai_custom_job_launcher",
)