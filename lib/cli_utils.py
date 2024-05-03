from termcolor import colored
from pyfiglet import Figlet
from InquirerPy import inquirer
import typer


def banner():
    f = Figlet(font='digital')
    print(f"{f.renderText('Nakalator')}")
    print("""This CLI allows you to send images to Nakala.\n© 2024 - ENC / Mission projets numériques\n""")


def cli_log(message, type_message="info", indicator="info"):
    type_color_map = {
        "info": "blue",
        "error": "red",
        "warning": "yellow",
        "success": "green",
    }

    type_emoji_map = {
        "noway": "🚫",
        "info": "",
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


def valid_method(method: str):
    if method.lower() not in ["soft", "hard", "go"]:
        raise typer.BadParameter("Method must be 'soft' or 'hard'")
    return method

def prompt_select(message, choices, default=None):
    return inquirer.select(
        message=message,
        choices=choices,
        default=default,
    ).execute()


def prompt_confirm(message, default=False):
    return inquirer.confirm(
        message=message,
        default=default,
    ).execute()