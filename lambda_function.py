import dns.resolver
import socket
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DNS_SERVER_IP = "10.0.1.10"      # EC2 private IP
TEST_DOMAIN = "google.com"
TIMEOUT = 3

def lambda_handler(event, context):
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [DNS_SERVER_IP]
        resolver.timeout = TIMEOUT
        resolver.lifetime = TIMEOUT

        answer = resolver.resolve(TEST_DOMAIN, "A")

        ips = [rdata.address for rdata in answer]
        logger.info(f"DNS OK - Resolved {TEST_DOMAIN} to {ips}") #This one does log 

        return {
            "status": "OK",
            "resolved_ips": ips
        }

    except Exception as e:
        logger.error(f"DNS CHECK FAILED: {str(e)}") #This one is going to log 

        # Optional: raise exception to trigger alarm
        raise