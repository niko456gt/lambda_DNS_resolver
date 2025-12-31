import socket
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)


TARGETS = [
    {"ip": "8.8.8.8", "port": 53, "name": "Google DNS"},

]

TIMEOUT = 3  # seconds

def check_connectivity(ip, port):
    try:
        start = time.time()
        sock = socket.create_connection((ip, port), timeout=TIMEOUT)
        latency = round((time.time() - start) * 1000, 2)
        sock.close()
        return {
            "status": "reachable",
            "latency_ms": latency
        }
    except socket.timeout:
        return {
            "status": "timeout",
            "latency_ms": None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def lambda_handler(event, context):
    results = {}

    for target in TARGETS:
        ip = target["ip"]
        port = target["port"]
        name = target["name"]

        logger.info(f"Checking connectivity to {name} ({ip}:{port})")

        result = check_connectivity(ip, port)
        results[name] = {
            "ip": ip,
            "port": port,
            **result
        }

        if result["status"] == "reachable":
            logger.info(f"OK - {name} reachable ({result['latency_ms']} ms)")
        else:
            logger.error(f"FAIL - {name} ({result})")

    return {
        "timestamp": int(time.time()),
        "results": results
    }
