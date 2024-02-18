#!/usr/bin/env python
"""
Decorators
"""
import sys
import logging
from .slack import send_to_slack
from .config import config

def notify(func):
    """
    Notify decorator to send message to Slack
    """
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as error:
            notifications_enabled = config.get_config_value(
                'GLBM_NOTIFICATIONS_ENABLED', default='true').lower()
            if notifications_enabled == 'true':
                logging.error(error)
                send_to_slack(error)
                sys.exit(1)
            else:
                logging.error(error)
                sys.exit(1)

    return wrapper
