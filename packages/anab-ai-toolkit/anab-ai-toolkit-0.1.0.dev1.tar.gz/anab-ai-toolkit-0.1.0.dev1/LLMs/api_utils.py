import random
from time import sleep


def exponential_backoff(func):
    """
    Decorator function that implements exponential backoff for retrying a function.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.

    Raises:
        Exception: If the maximum number of retries is reached.
    """
    def wrapper(*args, **kwargs):
        retries = 0
        while True:
            try:
                return func(*args, **kwargs)
            except:
                if retries >= 5:
                    raise
                sleep_time = random.uniform(0, 2 ** retries)
                sleep(sleep_time)
                retries += 1
    return wrapper