from enum import Enum
from os import makedirs
import os.path as op
from colorama import Style, Fore
from datetime import datetime


def check_dir(*args, dir_exist_ok=True) -> str:
    path = op.abspath(op.join(*args))
    if op.isfile(path):
        path, _ = op.split(path)
        # raise IOError(f'{path} is a file instead of a directory.')
    if not dir_exist_ok and op.isdir(path):
        raise IOError(f'{path} already exist.')
    makedirs(path, exist_ok=True)
    return path


def datetime_str():
    return datetime.isoformat(datetime.now())[:-4]

class MessageIntent(Enum):
    DEFAULT=0
    INFO=1
    SUCCESS=2
    ERROR=3
    WARNING=4
    HIGHLIGHT=5

def cprint(*args, intent:MessageIntent=MessageIntent.DEFAULT):
    """ Print a (optionally colored) message with the date and time"""
    if intent == MessageIntent.INFO: clr = Fore.BLUE
    elif intent == MessageIntent.SUCCESS: clr = Fore.GREEN
    elif intent == MessageIntent.ERROR: clr = Fore.RED
    elif intent == MessageIntent.WARNING: clr = Fore.YELLOW
    elif intent == MessageIntent.HIGHLIGHT: clr = Fore.LIGHTMAGENTA_EX
    else: clr = Fore.WHITE
    print(f'{datetime_str()}:', clr, " ".join(str(a) for a in args), Style.RESET_ALL)


def merge_dicts(a: dict, b: dict) -> dict():
    """ Override a with b values 

        If a keys dot not existe in b, it is created
    """
    for key in b:
        if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
            a[key] = merge_dicts(a[key], b[key])
        else:
            a[key] = b[key]
    return a
