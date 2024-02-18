import logging

log_format = '%(asctime)s| [%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
log = logging.getLogger(__name__)
