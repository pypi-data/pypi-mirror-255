import random
import socket

from clickhouse_driver import Client as CHClient, errors
from clickhouse_s3_etl_tools.logger import get_logger

logger = get_logger(__name__)


class Client(CHClient):
    def __init__(self, *args, reconnect=False, reconnect_attempts=10, **kwargs):
        super().__init__(*args, **kwargs)

        self.reconnect_attempts = reconnect_attempts or 1

        if reconnect:
            self.connection.force_connect = self.force_reconnect
        self.connection.connect = self.balanced_connect

    def force_reconnect(self):
        self.disconnect()
        if not self.connection.connected:
            self.connection.connect()

    def balanced_connect(self):
        conn = self.connection

        if conn.connected:
            conn.disconnect()

        logger.debug(f"Connecting. Database: {conn.database}. User: {conn.user}")

        err = None
        hosts_num = len(conn.hosts)
        reconnect_counter = 0
        while reconnect_counter <= self.reconnect_attempts:
            host_rnd = random.randint(0, hosts_num - 1)
            host, port = conn.hosts[host_rnd]
            logger.debug(f"Connecting to {host}:{port}")
            reconnect_counter += 1
            try:
                res = conn._init_connection(host, port)
                reconnect_counter = 0
                return res

            except socket.timeout as e:
                conn.disconnect()
                logger.warning(
                    f"Failed attempt #{reconnect_counter} to connect to {host}:{port}",
                    exc_info=True,
                )
                err = errors.SocketTimeoutError(
                    f"{e.strerror} ({conn.get_description()})"
                )

            except socket.error as e:
                conn.disconnect()
                logger.warning(
                    f"Failed attempt #{reconnect_counter} to connect to {host}:{port}",
                    exc_info=True,
                )
                err = errors.NetworkError(f"{e.strerror} ({conn.get_description()})")

        raise err
