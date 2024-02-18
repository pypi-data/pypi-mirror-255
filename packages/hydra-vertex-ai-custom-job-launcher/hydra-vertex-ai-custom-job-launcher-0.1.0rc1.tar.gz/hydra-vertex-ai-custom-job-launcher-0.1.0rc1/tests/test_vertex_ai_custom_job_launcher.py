from pytest import mark

from hydra.core.plugins import Plugins
from hydra.plugins.launcher import Launcher
from hydra.test_utils.launcher_common_tests import (
    IntegrationTestSuite,
    LauncherTestSuite,
)

from hydra_plugins.vertex_ai_custom_job_launcher.custom_job_launcher import VertexAICustomJobLauncher

def test_discovery() -> None:
    # Tests that this plugin can be discovered via the plugins subsystem when looking for Launchers
    assert VertexAICustomJobLauncher.__name__ in [
        x.__name__ for x in Plugins.instance().discover(Launcher)
    ]

@mark.parametrize("launcher_name, overrides", [("vertex_ai_custom_job", [])])
class TestVertexAICustomJobLauncher(LauncherTestSuite):
    """
    Run the Launcher test suite on this launcher.
    """
    pass

@mark.parametrize("task_launcher_cfg", [{"_target_": "vertex_ai_custom_job_launcher"}])
class TestVertexAICustomJobLauncherIntegration(IntegrationTestSuite):
    """
    Run the Integration test suite on this launcher.
    """
    pass