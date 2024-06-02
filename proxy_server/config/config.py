# Configuration

# Server
import socket


HOST = "127.0.0.1"
PORT = 55353
DNS_PORT = 53
ADDRESS = (HOST, PORT)
MAX_WORKERS = 10

# Socket
SOCKET_TYPE = socket.AF_INET
TRANSPORT_PROTOCOL = socket.SOCK_STREAM
PKG_SIZE = 1024
TIMEOUT_IN_SECONDS = 5

# DNS over TLS - CloudFlare
UPSTREAM_HOST = "1.1.1.1"
UPSTREAM_PORT = 853
WITH_TLS = 1

# Version
version = "0.1.0"
