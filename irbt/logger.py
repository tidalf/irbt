"""
Logger helpers functions.

Used for to set separate log levers depending of the loggers
"""
import logging
logging.basicConfig(level=logging.DEBUG)

urllib3_logger = logging.getLogger('urllib3.connectionpool')
urllib3_logger.setLevel(logging.ERROR)

mqtt_logger = logging.getLogger('AWSIoTPythonSDK.core')
mqtt_logger.setLevel(logging.ERROR)


def enable_mqtt_logging():
    """
    Enable Mqtt Logging.

    Set the mqtt logger to DEBUG when asked.
    """
    mqtt_logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    mqtt_logger.addHandler(stream_handler)
