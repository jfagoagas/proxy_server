from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
from proxy_server.lib.logger.logger import logger
from proxy_server.config.config import PKG_SIZE, SOCKET_TYPE, TRANSPORT_PROTOCOL


class ProxyServer:
    _listen_host: str
    _listen_port: int
    _upstream_host: str
    _upstream_port: str
    _sock: socket
    _thread_pool: ThreadPoolExecutor
    _futures: list

    def __init__(
        self,
        listen_host: str,
        listen_port: int,
        upstream_host: str,
        upstream_port: int,
        max_workers: int,
    ) -> "ProxyServer":
        self._listen_host = listen_host
        self._listen_port = listen_port

        self._upstream_host = upstream_host
        self._upstream_port = upstream_port

        # TODO: listen also in UDP
        self._sock = socket.socket(SOCKET_TYPE, TRANSPORT_PROTOCOL)

        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self._listen_host, self._listen_port))
        logger.info(
            f"DNS Proxy server listening at {self._listen_host}:{self._listen_port} ..."
        )
        self._sock.listen(1)

        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self._futures = []

    def start(self):
        with self.sock:
            try:
                while True:
                    client_connection, _ = self.sock.accept()

                    # Submit tasks to the thread pool
                    self._futures.append(
                        self._thread_pool.submit(
                            self.handle_client_request,
                            client_connection,
                        )
                    )
            except KeyboardInterrupt:
                logger.info("Stopping DNS Proxy server ...")

            except Exception as error:
                logger.error(error)

            finally:
                self.__stop__()

    def __stop__(self):
        for future in as_completed(self._futures):
            try:
                future.result()
            except Exception as error:
                logger.error(error)

    @property
    def listen_host(self) -> str:
        return self.listen_host

    @property
    def listen_port(self) -> str:
        return self._listen_port

    @property
    def upstream_host(self) -> str:
        return self._upstream_host

    @property
    def upstream_port(self) -> str:
        return self._upstream_port

    @property
    def sock(self) -> socket:
        return self._sock

    @property
    def thread_pool(self) -> ThreadPoolExecutor:
        return self._thread_pool

    def handle_client_request(self, connection):
        """
        Handle a client connection by receiving a data input, making an upstream TLS request to the specified host and port, and sending back the data response.

        Args:
            connection: The client connection to handle.

        Returns:
            None
        """
        with connection:
            data = connection.recv(PKG_SIZE)
            logger.info(f"> Input package \n{data}\n")

            response = self.make_upstream_request(
                data,
            )

            if not response:
                return

            logger.info(f"< Response package \n{response}\n")
            connection.sendall(response)
            return

    def make_upstream_request(self, data: bytes) -> bytes:
        """
        Make an upstream request to the specified host and port.

        Args:
            data (bytes): The data to be sent over the network.

        Returns:
            bytes: The response received after sending the request.
        """
        with socket.create_connection(
            (self._upstream_host, self._upstream_port)
        ) as conn:
            conn.sendall(data)
            response = conn.recv(PKG_SIZE)
            return response
