import socket
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SYSLOG_SERVER_IP = "18.204.215.41"
SYSLOG_PORT = 514
TIMEOUT = 3

def lambda_handler(event, context):
    message = (
        "<134>"
        f"LambdaSyslogHealthCheck "
        f"Test message at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(TIMEOUT)

        sock.sendto(message.encode("utf-8"), (SYSLOG_SERVER_IP, SYSLOG_PORT))
        sock.close()

        logger.info("Syslog OK - Test message sent successfully")

        return {"status": "OK"}

    except Exception as e:
        logger.error(f"Syslog FAILED - Unable to send log: {e}")
        raise
