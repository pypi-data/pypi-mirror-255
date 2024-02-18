#!/usr/bin/env python
"""
S3 Module
"""

import boto3
from .decorators import notify
from .config import config

@notify
def setup_s3():
    """
    S3 Setup session and set correct variables
    """
    env_vars = {
        "s3_bucket": config.get_config_value("GLBM_S3_BUCKET"),
        "s3_endpoint": config.get_config_value("GLBM_S3_ENDPOINT_URL"),
        "s3_directory": config.get_config_value("GLBM_S3_DIRECTORY")
    }

    for var_name, value in env_vars.items():
        if value is None:
            raise Exception(f"Missing {var_name} from config of OS env var.")

    days_to_keep = config.get_config_value("GLBM_DAYS_TO_KEEP", 30)

    session = boto3.Session()

    # Create an S3 client object using the session
    s3 = session.client('s3', endpoint_url=env_vars['s3_endpoint']) # pylint: disable=invalid-name

    return s3, env_vars['s3_bucket'], env_vars['s3_directory'], days_to_keep, env_vars['s3_endpoint']
