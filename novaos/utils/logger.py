import logging
import os

LOG_FILE = "novaos.log"

def setup_logger():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def log_info(message: str):
    logging.info(message)

def log_error(message: str):
    logging.error(message)
    
    
# create novaos.log file store log and make logging  proffessionallyy