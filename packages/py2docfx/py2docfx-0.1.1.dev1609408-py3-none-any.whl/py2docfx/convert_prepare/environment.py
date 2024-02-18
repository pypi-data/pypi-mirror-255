import subprocess

REQUIREMENT_MODULES = ["setuptools", "sphinx==6.1.3", "pyyaml", "jinja2==3.0.3"]


def install_converter_requirements():
    """
    Install setuptools/sphinx/pyyaml/jinja2
    Replacing logic of
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/Python/InstallPackage.ps1&line=15&lineEnd=35&lineStartColumn=1&lineEndColumn=87&lineStyle=plain&_a=contents
    """
    pip_install_cmd = ["python", "-m", "pip", "install", "--upgrade"]

    pip_install_common_options = [
        "--no-cache-dir",
        "--quiet",
        "--no-compile",
        "--no-warn-conflicts",
        "--disable-pip-version-check",
    ]

    for module in REQUIREMENT_MODULES:
        print(f"<CI INFO>: Upgrading {module}...")
        subprocess.run(
            pip_install_cmd + [module] + pip_install_common_options, check=True
        )
