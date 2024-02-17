import subprocess
import os.path as op
from time import time
from datetime import datetime
from typing import Iterable, List, Union
from .utils import MessageIntent, cprint
import sys
import traceback


def write_log(log_f, *text: Union[str, List[str]]):
    """ Append text to the log text file. """
    # text = [text] if isinstance(text, str) else text
    with open(log_f, 'a+') as fp:
        fp.writelines(text)

def get_versions():
    return {
        "python": f"{sys.version[0]}.{sys.version[1]}"
    }


def versions_2_txt(versions:dict=None):
    txt = "### Versions:\n"
    if versions is not None:
        for k, v in versions.items():
            txt += f"{k}: {v}\n"
    txt += "#############\n"
    return txt
    

def run_cmd(cmd, title=None, log=None, versions:dict=None, raise_errors=True):
    """ Run a command in a sub process """
    splitted_cmd = cmd #cmd.split(' ')

    if title:
        cprint(f"Start {title}", intent=MessageIntent.INFO)
    cprint(cmd)
    tic = time()
    try:
        if log:
            write_log(log, 
                "\n",
                "#" * 80,
                f"\n####### {title} ######\n",
                versions_2_txt(versions),
                cmd,
                f"\n##########\nStarted at: {datetime.isoformat(datetime.now())}"
            )
            tic = time()
            output = subprocess.check_output(splitted_cmd, stderr=subprocess.STDOUT, shell=True)
            toc = time()
            write_log(log,
                output.decode("utf-8"),
                f"\nFinshed at: {datetime.isoformat(datetime.now())} - tooks {toc-tic:.03f}s",
                "\n#####\n\n\n"
            )
        else:
            subprocess.run(splitted_cmd, shell=True)
    except Exception as e:
        tb = traceback.format_exc()
        cprint(f"An error occured while running: {cmd}", intent=MessageIntent.ERROR)
        if log:
            write_log(log,
                f"Errored at {datetime.isoformat(datetime.now())}:\n",
                str(e), "\n#####\n\n\n"
            )
        if raise_errors:
            raise e
        else:
            cprint(str(e), intent=MessageIntent.ERROR)
            cprint(tb, intent=MessageIntent.ERROR)
            return -1
    if log:
        cprint(f'Console outputs saved to:', log, intent=MessageIntent.INFO)
    if title:
        cprint(f"{title} tooks {time()-tic:.02f}s", intent=MessageIntent.SUCCESS)
    else:
        cprint(f"done in {time()-tic:.02f}s", intent=MessageIntent.SUCCESS)
    return 0


def cached_run(cmd, out_files:List[str]=None, title=None, log=None, 
               versions:dict=None, raise_errors=True, verbose=False):
    """ Run the command only if one of the out_files is missing """
    if isinstance(out_files, str):
        out_files = [out_files]

    do_run = False
    if out_files is not None:
        for f in out_files:
            if not op.isfile(f) and not op.isdir(f):
                do_run = True
                break
    
    if do_run:
        return run_cmd(cmd, title, log, versions, raise_errors)
    if verbose:
        cprint('Using cached files for', title if title else cmd, intent=MessageIntent.WARNING)


def _run_func(func, args):
    if args is None:
        func()
    elif isinstance(args, dict):
        func(**args)
    elif isinstance(args, Iterable):
        func(*args)
    else:
        raise ValueError("arguments hould be either None, a list or a dict.")
 

def run_func(func, args, title=None, log=None, versions:dict=None, raise_errors=True):
    """ Run a command in a sub process """
    if title:
        cprint(f"Start {title}", intent=MessageIntent.INFO)
    cprint(func.__name__)
    cprint('args:\n')
    for arg in args:
        cprint('\t', arg)

    tic = time()
    try:
        if log:
            write_log(log, 
                "\n",
                "#" * 80,
                f"\n####### {title} ######\n",
                versions_2_txt(versions),
                func.__name__ if hasattr(func, '__name__') else func,
                f"\n##########\nStarted at: {datetime.isoformat(datetime.now())}"
            )
            tic = time()
            _run_func(func, args)
            toc = time()
            write_log(log,
                f"\nFinshed at: {datetime.isoformat(datetime.now())} - tooks {toc-tic:.03f}s",
                "\n#####\n\n\n"
            )
        else:
            _run_func(func, args)
    except Exception as e:
        tb = traceback.format_exc()
        cprint(f"An error occured while running: {func.__name__}", intent=MessageIntent.ERROR)
        cprint(str(e), intent=MessageIntent.ERROR)
        if log:
            write_log(log,
                f"Errored at {datetime.isoformat(datetime.now())}:\n",
                str(e), "\n#####\n\n\n"
            )
        if raise_errors:
            raise e
        else:
            cprint(str(e), intent=MessageIntent.ERROR)
            cprint(tb, intent=MessageIntent.ERROR)
            return -1
    if log:
        cprint(f'Console outputs saved to:', log, intent=MessageIntent.INFO)
    if title:
        cprint(f"{title} tooks {time()-tic:.02f}s", intent=MessageIntent.SUCCESS)
    else:
        cprint(f"done in {time()-tic:.02f}s", intent=MessageIntent.SUCCESS)
    return 0


def cached_function_call(func, args, out_files:List[str]=None, title=None, log=None, 
                         versions:dict=None, raise_errors=True, verbose=False):
    """ Run python function only if one of the out_files is missing """
    if isinstance(out_files, str):
        out_files = [out_files]

    do_run = False
    if  out_files is not None:
        for f in out_files:
            if not op.isfile(f) and not op.isdir(f):
                do_run = True
                break
    
    if do_run:
        return run_func(func, args, title, log, versions, raise_errors)
    if verbose:
        cprint('Using cached files for', title if title else func.__name__, intent=MessageIntent.WARNING)
