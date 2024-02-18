import threading
from logging import Logger

def initialize_threading(logger: Logger):
    def exception_hook(args):
        # Check if the necessary attributes are present in args
        if hasattr(args, 'exc_type') and hasattr(args, 'exc_value') and hasattr(args, 'exc_traceback'):
            # Log the exception with traceback
            logger.error("Uncaught exception occurred in thread:", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
        else:
            # Fallback message if the expected attributes are not found
            logger.error("Uncaught exception occurred in thread, but exception details are unavailable")

    threading.excepthook = exception_hook