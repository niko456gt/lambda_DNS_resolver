import socket
import struct
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

NTP_SERVER = "10.0.6.44"   # Your EC2 NTP server IP or hostname
NTP_PORT = 123
TIMEOUT = 3
MAX_DRIFT_SECONDS = 300  # 5 minutes

def get_ntp_time(server):
    """
    Query NTP server and return UNIX timestamp
    """
    msg = b'\x1b' + 47 * b'\0'  # NTP request packet

    addr = (server, NTP_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    try:
        sock.sendto(msg, addr)
        data, _ = sock.recvfrom(48)
    finally:
        sock.close()

    # NTP timestamp starts at byte 40
    ntp_time = struct.unpack("!12I", data)[10]

    # Convert NTP time (1900 epoch) to UNIX epoch (1970)
    return ntp_time - 2208988800

def lambda_handler(event, context):
    try:
        ntp_time = get_ntp_time(NTP_SERVER)
        local_time = time.time()

        drift = abs(local_time - ntp_time)

        logger.info(
            f"NTP OK - Drift: {int(drift)} seconds "
            f"(Local={int(local_time)}, NTP={int(ntp_time)})"
        )

        if drift > MAX_DRIFT_SECONDS:
            logger.error(
                f"NTP DRIFT EXCEEDED - {int(drift)} seconds "
                f"(threshold {MAX_DRIFT_SECONDS})"
            )
            raise Exception("NTP drift exceeds threshold")

        return {
            "status": "OK",
            "drift_seconds": int(drift)
        }

    except Exception as e:
        logger.error(f"NTP CHECK FAILED: {e}")
        raise
