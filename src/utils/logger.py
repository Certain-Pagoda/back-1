import sys
import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") 

def create_logger(name):
    """ Logger configuration
    """
    log = logging.getLogger(name)
    log.setLevel(getattr(logging, LOG_LEVEL))
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, LOG_LEVEL))
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

    return log
