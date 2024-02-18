import datetime
import logging
import uuid
from threading import Thread, Timer
from urllib.parse import urlencode

# to ignore connection pool warning
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


def generate_uuid() -> str:
    return str(uuid.uuid1())


def get_current_utc_timestamp() -> float:
    """
    Get current time in UTC timestamp format

    Returns:
        float: current time in UTC timestamp format
    """
    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    return utc_time.timestamp()


def generate_query_url(url: str, dict_query_params: dict):
    """
    Generate a query string for use with a REST API endpoint.
    This function generates the necessary query string from the provided dictionary for use with a REST API endpoint.

    Args:
        url (str): The REST API domain + endpoint.
        dict_query_params (dict): A dictionary containing all parameter names and values to be included in the query string.

    Returns:
        str: The original URL with a query string appended to it derived from the dictionary provided.
    """
    url += "?"

    params = []
    for key, val in dict_query_params.items():
        if isinstance(val, list):
            list_query_str = urlencode([(key, element) for element in val])
            params.append(list_query_str)
            continue

        params.append(str(key) + "=" + str(val))

    url += "&".join(params)
    return url


def create_thread(func: object | None, args: tuple) -> Thread:
    """
    Create and start a daemon thread for the specified function and arguments.

    Args:
        func (object | None): The function name. Do not invoke it; leave out the "()".
        args (tuple): The tuple of the function's arguments.

    Returns:
        Thread: The Thread object.
    """
    t = Thread(target=func, args=args)
    t.daemon = True
    return t


def create_thread_with_kwargs(func: object | None, kwargs: dict) -> Thread:
    """
    Create and start a daemon thread for the specified function and arguments.

    Args:
        func (object | None): The function name. Do not invoke it; leave out the "()".
        kwargs (dict): The dictionary of the function's arguments.

    Returns:
        Thread: The Thread object.
    """

    t = Thread(target=func, kwargs=kwargs)
    t.daemon = True
    return t


def get_default_logger():
    """
    Create a default logger

    Returns:
        default logger
    """
    default_logger = logging
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # Create a stream handler and set the formatter
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    default_logger.basicConfig(level=logging.INFO, handlers=[stream_handler])
    return default_logger


def create_logger(logger_level: int = logging.INFO, logger_name: str = "infinity_client") -> logging.Logger:
    """
    Create a logger with the specified logger level and name.

    Args:
        logger_level (int, optional): The logger level. Defaults to logging.INFO.
        logger_name (str, optional): The logger name. Defaults to "infinity_client".

    Returns:
        logging.Logger: The Logger object.
    """
    logging.basicConfig(level=logger_level)
    logger = logging.getLogger(logger_name)
    # Create a formatter with the desired format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # Create a stream handler and set the formatter
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


class RepeatTimer(Timer):
    def run(self):
        """
        Override the run method of Timer class.

        This method is called when the timer is started and it repeatedly calls the specified function with the provided arguments.
        """
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
