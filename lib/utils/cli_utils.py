# -- coding: utf-8 --

"""cli_utils.py

This module contains the functions to interact with the user in the CLI.
"""

from typer import echo
from pyfiglet import Figlet
from InquirerPy import inquirer
from wasabi import Printer

# Create a printer object to display messages in the CLI with wasabi
msg = Printer()

def cli_log(message: str, type_message: str="info") -> None:
    """Display a message in the CLI
    :param message: the message to display
    :type message: str
    :param type_message: the type of message (default: "info")
    :type type_message: str
    :return: None
    :rtype: None
    """
    if type_message == "info":
        message = msg.info(message)
    elif type_message == "error":
        message = msg.fail(message)
    elif type_message == "warning":
        message = msg.warn(message)
    elif type_message == "success":
        message = msg.good(message)
    echo(message)


def banner() -> None:
    """Display the banner of the CLI
    :return: None
    :rtype: None
    """
    f = Figlet(font='digital')
    print(f"{f.renderText('Nakalator')}")
    print("""This CLI allows you to send images to Nakala.\n© 2024 - ENC / Mission projets numériques\n""")


def prompt_select(message: str, choices: list, default: str) -> str:
    """Prompt the user to select an option from a list of choices.
    :param message: a message to display to the user
    :type message: str
    :param choices: a list of choices
    :type choices: list
    :param default: the default choice
    :type default: str
    :return: the selected choice
    :rtype: str
    """
    return inquirer.select(
        message=message,
        choices=sorted(choices),
        default=default,
    ).execute()


def prompt_confirm(message: str, default: bool = False):
    return inquirer.confirm(
        message=message,
        default=default,
    ).execute()


"""
Replace by wasabi package
def cli_log(message, type_message="info", indicator="info"):
    type_color_map = {
        "info": "blue",
        "error": "red",
        "warning": "yellow",
        "success": "green",
    }

    type_emoji_map = {
        "noway": "🚫",
        "info": "ℹ️",
        "error": "❌",
        "warning": "⚠️",
        "success": "✅",
        "retry": "🔁",
        "timer": "⏳",
        "time": "⏰",
        "check_good": "✅",
        "check_bad": "❌",
        "check_question": "❓",
        "good": "👍",
        "pkg": "📦",
        "look": "🔍"
    }
    return colored(f"{type_emoji_map[indicator]}\t{message}", type_color_map[type_message])
"""
