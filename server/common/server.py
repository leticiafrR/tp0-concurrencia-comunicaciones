import os
import socket
import logging
import signal
from .server_protocol import ServerProtocol
from typing import Optional
from .utils import store_bets


class Server:
    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.protocol: Optional[ServerProtocol] = None
        self._keep_running = True
        self.__register_signal_handlers()

    def __register_signal_handlers(self):
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

    def shutdown(self, signum, frame):
        self._keep_running = False
        self._server_socket.close()
        logging.info("action: close_connection | result: success")
        if self.protocol is not None:
            self.protocol.shutdown()
            logging.info("action: close_connection | result: success")
        os._exit(0)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communication
        finishes, servers starts to accept new connections again
        """
        while self._keep_running:
            try:
                peer = self.__accept_new_connection()
                self.protocol = ServerProtocol(peer)
                self.__handle_client_connection()
            except Exception as e:
                logging.error(f"action: iteration | result: fail | error: {e}")
                break

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        if self.protocol is None:
            return 

        try:
            bet = self.protocol.receiveBet()
            logging.info(f'action: apuesta_recibida | result: success | dni: {bet.document} | numero: {bet.number} | fecha_nacimiento: {bet.birthdate}')
            store_bets([bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
            self.protocol.sendConfirmation(True)
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            self.protocol.shutdown()


    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
