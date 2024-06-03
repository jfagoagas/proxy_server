import socket
import ssl

# import struct

from proxy_server.lib.proxy_server.proxy_server import ProxyServer


class ToTLS(ProxyServer):
    _tls_context: ssl.SSLContext

    def __init__(
        self,
        listen_host: str,
        listen_port: int,
        upstream_host: str,
        upstream_port: int,
        max_workers: int,
        purpose=ssl.Purpose.SERVER_AUTH,
        tls_minimum_version=ssl.TLSVersion.TLSv1_3,
    ) -> "ToTLS":
        super().__init__(
            listen_host, listen_port, upstream_host, upstream_port, max_workers
        )
        self._tls_context = ssl.create_default_context(purpose)
        self._tls_context.minimum_version = tls_minimum_version

    def make_upstream_request(self, data: bytes) -> bytes:
        """
        Make an upstream TLS request to the specified host and port.

        Args:
            data (bytes): The data to be sent over TLS.

        Returns:
            bytes: The response received after sending the DNS query over TLS.
        """
        # TODO: add error handling while reading from the socket
        with socket.create_connection(
            (self._upstream_host, self._upstream_port)
        ) as conn:
            with self._tls_context.wrap_socket(
                conn, server_hostname=self._upstream_host
            ) as tls_sock:
                # The DNS over TLS protocol encapsulates DNS messages within a TLS record, and each DNS message is prefixed by a 2-byte
                # length field that specifies the length of the DNS message, https://datatracker.ietf.org/doc/html/rfc7858#section-3.3.
                # This length prefix ensures that the receiving end knows the exact boundaries
                # of the DNS message within the stream.

                # Send DNS over TLS - Each DNS message is preceded by a 2-byte (big-endian - network) length prefix,
                # TCP complies with that format, UDP needs to prepend the 2-byte package length.
                tls_sock.sendall(data)

                # The response can have \x00 if the client specifies to use EDNS, which includes padding.
                # This padding is used to obscure the actual size of DNS messages to
                # mitigate certain types of attacks and enhance privacy.

                # Get the response
                response = tls_sock.recv()

                # Read the length of the response
                # In UDP we remove the 2-byte length from the DNS Over TLS response
                # response_length = struct.unpack("!H", tls_sock.recv(2))[0]
                # response = tls_sock.recv()

        return response
