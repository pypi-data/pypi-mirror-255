from setuptools import find_namespace_packages, setup
import re

def get_version():
    with open('hydra_plugins/vertex_ai_custom_job_launcher/__init__.py', 'r') as file:
        return re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", file.read(), re.M).group(1)
    
def get_requirements():
    """
    Read the requirements from the __init__.py file at __requirements__ variable
    """
    # Read the file
    with open('hydra_plugins/vertex_ai_custom_job_launcher/__init__.py', 'r') as file:
        # Get the string that is between "__requirements__ = [" and ]
        requirements_str = re.search(r"^__requirements__ = \[([^\]]*)\]", file.read(), re.M).group(1)
        # Split the string by comma and remove the quotes
        return [req.strip().replace('"', '') for req in requirements_str.split(',')]

with open("README.md") as fh:
    LONG_DESC = fh.read()
    setup(
        name="hydra-vertex-ai-custom-job-launcher",
        version=get_version(),
        packages=find_namespace_packages(include=["hydra_plugins.*"]),
        description="Hydra Vertex AI Launcher plugin",
        long_description=LONG_DESC,
        long_description_content_type="text/markdown",
        author="Paul Beuran",
        author_email="paul.beuran@outlook.fr",
        url="https://github.com/PaulBeuran/hydra-vertex-ai-custom-job-launcher",
        classifiers=[
            # Feel free to use another license.
            "License :: OSI Approved :: MIT License",
            # Hydra uses Python version and Operating system to determine
            # In which environments to test this plugin
            "Programming Language :: Python :: 3.10",
            "Operating System :: OS Independent",
        ],
        install_requires=get_requirements(),
        # If this plugin is providing configuration files, be sure to include them in the package.
        # See MANIFEST.in.
        # For configurations to be discoverable at runtime, they should also be added to the search path.
        include_package_data=True,
    )