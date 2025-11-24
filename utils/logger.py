import logging

def setup_logger(log_file):
    logger = logging.getLogger("FileTransferLogger")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)