import logging
import os

import graypy


def get_default_log(instance_name):
    logger = logging.getLogger(f"crawling_{instance_name}_log")
    logger.setLevel(logging.INFO)

    if os.getenv("GRAYLOG_ENABLE") == "TRUE":
        if os.getenv("GRAYLOG_TLS") == "TRUE":
            handler = graypy.GELFTLSHandler(
                os.getenv("GRAYLOG_ADDR"), int(os.getenv("GRAYLOG_PORT"))
            )
        else:
            handler = graypy.GELFTCPHandler(
                os.getenv("GRAYLOG_ADDR"), int(os.getenv("GRAYLOG_PORT"))
            )
        logger.addHandler(handler)
        logger.addHandler(logging.StreamHandler())

    return logger
