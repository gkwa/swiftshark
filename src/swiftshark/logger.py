"""Logging module for swiftshark."""

import logging
import sys


def setup_logging(verbosity: int) -> int:
    """Set up logging with the appropriate verbosity level.

    Args:
        verbosity: The verbosity level (0-3)

    Returns:
        The configured verbosity level
    """
    # Cap verbosity at 3
    verbosity = min(verbosity, 3)

    # Set up log levels based on verbosity
    log_levels = {
        0: logging.ERROR,  # Default: only errors
        1: logging.WARNING,  # -v: warnings and errors
        2: logging.INFO,  # -vv: info, warnings, and errors
        3: logging.DEBUG,  # -vvv: debug and all above
    }

    log_level = log_levels.get(verbosity, logging.ERROR)

    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format="[%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    # Create a logger for this module
    logger = logging.getLogger(__name__)
    logger.debug(
        f"Logging initialized with verbosity level: {verbosity} (log level: {logging.getLevelName(log_level)})"
    )

    return verbosity
