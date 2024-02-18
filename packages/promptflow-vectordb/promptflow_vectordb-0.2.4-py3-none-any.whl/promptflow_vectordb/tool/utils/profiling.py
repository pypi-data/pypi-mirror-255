import contextlib
import logging
from time import perf_counter
from typing import Callable


@contextlib.contextmanager
def measure_execution_time(activity_name: str, callback: Callable = None):
    try:
        start_time = perf_counter()
        yield
    finally:
        end_time = perf_counter()
        log_message = f'`{activity_name}` completed in {end_time - start_time} seconds.'
        if callback:
            callback(log_message)
        else:
            logging.info(log_message)
