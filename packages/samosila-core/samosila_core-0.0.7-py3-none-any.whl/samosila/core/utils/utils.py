import base64
import logging
import time

import numpy as np

# Create a logger object
logger: logging.Logger = logging.getLogger(__name__)

# Set the logging level
logger.setLevel(logging.INFO)

# Create a file handler
file_handler = logging.FileHandler('logs.log')
console_handler = logging.StreamHandler()

# Set the logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def trim_string(string, count: int) -> str:
    words = string.split()
    trimmed_words = words[:count]
    trimmed_string = ' '.join(trimmed_words)
    return trimmed_string

def run_with_time(func):
    start_time = time.time()

    func()

    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(execution_time)


def mp3_to_base64(file_path):
    with open(file_path, 'rb') as binary_file:
        binary_data = binary_file.read()
        base64_data = base64.b64encode(binary_data)
        base64_message = base64_data.decode('utf-8')
    return base64_message


def numpy_to_base64(array: np.ndarray) -> str:
    return base64.b64encode(array).decode('utf-8')


def base64_to_numpy(base64_str: str) -> np.ndarray:
    return np.frombuffer(base64.b64decode(base64_str), dtype=np.float32)
