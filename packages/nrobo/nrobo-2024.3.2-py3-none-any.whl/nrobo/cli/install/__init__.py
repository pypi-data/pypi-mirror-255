import os
import shutil

from nrobo.cli.cli_constansts import nCLI, PACKAGES

from nrobo.util.process import terminal
from nrobo.util.python import __PYTHON__, __PIP__

__REQUIREMENTS__ = "requirements.txt"


def copy_dir(src, dest):
    try:
        shutil.copytree(src, dest)
    except FileExistsError as e:
        print(e)


def copy_file(src, dest):
    try:
        shutil.copyfile(src, dest)
    except FileExistsError as e:
        print(e)


def install_nrobo(requirements_file=None):
    """
    Install nrobo

    :return:
    """
    # Find the directory we executed the script from:
    execution_dir = os.getcwd()

    # Find the directory in which the current script resides:
    file_dir = os.path.dirname(os.path.realpath(__file__))

    import re
    path_nrobo = re.findall(r"(.*nrobo)", str(file_dir))

    from nrobo.cli import STYLE
    from nrobo.cli.tools import console

    console.rule(f"[{STYLE.HLOrange}]Welcome to NROBO install")
    with console.status(f"[{STYLE.HLGreen}]Installing requirements"):
        if requirements_file is None:
            requirements_file = __REQUIREMENTS__

        try:
            if os.path.exists(__REQUIREMENTS__):
                requirements_file = __REQUIREMENTS__
        except Exception as e:
            if os.path.exists(
                    PACKAGES.NROBO + os.sep + PACKAGES.CLI + os.sep + nCLI.INSTALL + os.sep + __REQUIREMENTS__):
                requirements_file = PACKAGES.NROBO + os.sep + PACKAGES.CLI + os.sep + nCLI.INSTALL + os.sep + __REQUIREMENTS__

        terminal([__PIP__, nCLI.INSTALL, '-r', requirements_file])

    with console.status(f"[{STYLE.HLGreen}]Installing framework"):
        # create framework folders on host system

        # Copy framework to current directory
        copy_dir(f"{path_nrobo[0]}{os.sep}framework{os.sep}pages", f"{execution_dir}{os.sep}pages")
        copy_dir(f"{path_nrobo[0]}{os.sep}framework{os.sep}tests", f"{execution_dir}{os.sep}tests")
        copy_dir(f"{path_nrobo[0]}{os.sep}browserConfigs", f"{execution_dir}{os.sep}browserConfigs")

        # Copy conftest.py and other files to current directory
        copy_file(f"{path_nrobo[0]}{os.sep}framework{os.sep}__init__.py", f"{execution_dir}{os.sep}")
        copy_file(f"{path_nrobo[0]}{os.sep}conftest.py", f"{execution_dir}{os.sep}")

    console.status(f"[{STYLE.PURPLE4}]Installation complete")
