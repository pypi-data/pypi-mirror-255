#!/usr/bin/env python
"""
Logging Module
"""

import os
import logging

LOGGING_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
}

def setup_logging():
    """
    Setup logging
    """

    logging_level = os.environ.get('GLBM_LOGGING_LEVEL', "INFO").upper()

    logging.basicConfig(
            format='%(asctime)s %(levelname)-4s - %(message)s',
            level=LOGGING_LEVELS.get(logging_level),
            datefmt='%Y-%m-%d %H:%M:%S',
            force=True
            )

    credentials_logger = logging.getLogger('botocore.credentials')
    credentials_logger.setLevel(logging.ERROR)
