from typing_extensions import Annotated
import typer

from proxy_server.config.config import (
    HOST,
    MAX_WORKERS,
    PORT,
    UPSTREAM_HOST,
    UPSTREAM_PORT,
    WITH_TLS,
)
from proxy_server.lib.proxy_server.proxy_server import ProxyServer
from proxy_server.lib.to_tls.to_tls import ToTLS


def proxy_server(
    host: Annotated[str, typer.Argument(envvar="HOST")] = HOST,
    port: Annotated[int, typer.Argument(envvar="PORT")] = PORT,
    upstream_host: Annotated[
        str, typer.Argument(envvar="UPSTREAM_HOST")
    ] = UPSTREAM_HOST,
    upstream_port: Annotated[
        int, typer.Argument(envvar="UPSTREAM_PORT")
    ] = UPSTREAM_PORT,
    max_workers: Annotated[int, typer.Argument(envvar="MAX_WORKERS")] = MAX_WORKERS,
    with_tls: Annotated[bool, typer.Argument(envvar="WITH_TLS")] = WITH_TLS,
):

    if with_tls:
        tls_proxy_server = ToTLS(host, port, upstream_host, upstream_port, max_workers)
        tls_proxy_server.start()
    else:
        proxy_server = ProxyServer(
            host, port, upstream_host, upstream_port, max_workers
        )
        proxy_server.start()


# Security Concerns
# Man in the middle from client to proxy
# TLS Protocol Vulnerabilities
# Certificate Validation
# Implementation Issues
# Operational Concerns - Availability, Single Point of Failure
# DNSSEC Support
# Server Security
# With DNS Over HTTPS all traffic goes to the 443 port, instead of 853
