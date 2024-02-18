import logging
from nexus_writer_service.utils import logging_utils


def config_root_logger():
    logger = logging.getLogger("nexus_writer_service")
    logging_utils.cliconfig(logger)
