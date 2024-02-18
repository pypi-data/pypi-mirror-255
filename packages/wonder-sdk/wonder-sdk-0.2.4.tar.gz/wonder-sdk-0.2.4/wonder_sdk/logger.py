import logging
import sys

def setup_logger() -> logging.Logger:
	"""
    Sets up a logger that logs messages of different severities to stdout and stderr.

    The logger is set to the DEBUG level. It propagates messages to two stream handlers:

    1. A handler for stdout: This handler handles messages that are less severe than WARNING (i.e., DEBUG and INFO messages).
    2. A handler for stderr: This handler handles messages that are WARNING or more severe (i.e., WARNING, ERROR, and CRITICAL messages).

    Returns
    -------
    logging.Logger
        A logger instance configured to log messages to stdout and stderr.
    """

	logger = logging.getLogger(__name__)
	logger.propagate = False

	stdout_handler = logging.StreamHandler(sys.stdout)
	stdout_handler.setLevel(logging.DEBUG)
	stdout_handler.addFilter(lambda r: r.levelno < logging.WARNING)
	logger.addHandler(stdout_handler)

	stderr_handler = logging.StreamHandler(sys.stderr)
	stderr_handler.setLevel(logging.DEBUG)
	stderr_handler.addFilter(lambda r: r.levelno >= logging.WARNING)
	logger.addHandler(stderr_handler)
	logger.setLevel(logging.DEBUG)

	return logger