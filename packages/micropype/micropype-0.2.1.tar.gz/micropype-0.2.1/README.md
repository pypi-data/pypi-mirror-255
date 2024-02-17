# MicroPype
A tiny package to create very basic pipeline executing command lines and/or calling python functions.

## Install
```shell
pip install micropype
```

## API
Here are the two mains functions you need:
### cached_run
Use it to execute a cammand line.
#### Arguments:
* **cmd**: Command line
* **out_files**: One or a list of file path(s) that are created by the command.
* **title**:(str, default: None) - A title 
* **log**: (str, default: None) - A path to a log file (text file)
* **versions**: (dict, default: None) - A dictionnary giving all the versions that must be logged
* **raise_errors**: (bool, default: True) - Wether to raise python error if the command failed (if True) or just print error in the console and continue (if False)

### cached_function_call
Use it to call a python function.
#### Arguments:
* **func**: A callable python object (function)
* **args**: List of the arguments
* **out_files**: One or a list of file path(s) that are created by the command.
* **title**:(str, default: None) - A title 
* **log**: (str, default: None) - A path to a log file (text file)
* **versions**: (dict, default: None) - A dictionnary giving all the versions that must be logged
* **raise_errors**: (bool, default: True) - Wether to raise python error if the command failed (if True) or just print error in the console and continue (if False)

## Configuration file


## Example
Here is an example of simple configuration file:
```yaml
steps:
    do_ls: true
    do_myfunction: false
```

And then the pipeline:
```python
from micropipe import cached_run, cached_function_call

log = "mylog.txt"

out_f = "lsOutput.log"
cached_run(
    f"ls -lrt >> {out_f}",
    out_f,
    "Listing current folder items",
    log_f
)

cached_function_call(
    myfuntion,
    [arg1, arg2],
    [file_1, file_2],
    title=f"Executing a python function",
    log=log_f
)
```