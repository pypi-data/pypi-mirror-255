import atexit
from time import time, strftime, localtime
from datetime import timedelta
from functools import wraps
from typing import Callable, Optional

# Configuration class to hold custom settings
class Config:
    custom_logger: Optional[Callable[[str], None]] = None
    time_format: str = "%Y-%m-%d %H:%M:%S"

def secondsToStr(elapsed: Optional[float] = None) -> str:
    if elapsed is None:
        return strftime(Config.time_format, localtime())
    else:
        return str(timedelta(seconds=elapsed))

def log(s: str, elapsed: Optional[str] = None) -> None:
    line = "=" * 40
    message = f"{line}\n{secondsToStr()} - {s}\n"
    if elapsed:
        message += f"Elapsed time: {elapsed}\n"
    message += line + "\n"
    
    if Config.custom_logger:
        Config.custom_logger(message)
    else:
        print(message)

def timing(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        elapsed = end - start
        log(f"Function {func.__name__} finished", secondsToStr(elapsed))
        return result
    return wrapper

# Functions to set custom logger and time format
def set_custom_logger(logger_func: Callable[[str], None]) -> None:
    Config.custom_logger = logger_func

def set_time_format(format_str: str) -> None:
    Config.time_format = format_str
