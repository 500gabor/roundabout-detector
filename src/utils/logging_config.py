import logging
import time


logging.basicConfig(
    filename=f"../logs/logfile_{time.strftime('%Y_%m_%d_%Hh%Mm%Ss')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

global_logger = logging.getLogger("test_assignment")
