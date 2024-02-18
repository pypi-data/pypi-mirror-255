"""
Trigger for nrobo framework!

"""
from nrobo.util.process import terminal

terminal(["pip", "install", "rich"])

import argparse
import time

import os

from nrobo.cli.install import install_nrobo, __REQUIREMENTS__
from nrobo.util.commands.ncommands import clear_screen, remove_files_recursively
from nrobo.util.constants import CONST
from nrobo.util.python import verify_set_python_install_pip_command
from nrobo.cli.tools import console
from nrobo.cli.formatting import themes as th, STYLE
from nrobo.cli.cli_constansts import nCLI as CLI, NREPORT
from nrobo.cli.cli_args import parse_cli_args

# refer to global defined in nrobo.util.process
global __PYTHON__
__APP_NAME__ = CONST.EMPTY


def greet_the_guest():
    greet_msg = 'Namastey Wolrd!. Thank you for choosing, NROBO.'.format(CONST.NEWLINE)
    formatted_heart_string = CONST.HEART_RED * (len(greet_msg) // 2)

    console.print(f'\n[{STYLE.HLRed}]{formatted_heart_string}'
                  f'\n[{STYLE.HLOrange}]{greet_msg}'
                  f'\n[{STYLE.HLRed}]{formatted_heart_string}')
    console.print(f'\n[{STYLE.PURPLE4}]We are still in the process of refactoring next gen nrobo.'
                  '\nStay tuned!\n')


def main():
    """
    Entry point of nrobo command-line-utility.

    :return:
    """

    clear_screen()
    greet_the_guest()
    install_nrobo()
    verify_set_python_install_pip_command()
    remove_files_recursively("dist")
    remove_files_recursively(NREPORT.REPORT_DIR)
    parse_cli_args()
