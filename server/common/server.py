import os
import socket
import logging
import signal
from typing import Optional



class Server:
    def __register_signal_handlers(self):
        signal.signal(signal.SIGTERM, self.shutdown)

    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._current_peer: Optional[socket.socket] = None
        self._is_client_closed = False
        self._keep_running = True
        self.__register_signal_handlers()

    def shutdown(self, signum, frame):
        self._keep_running = False
        self._server_socket.close()
        logging.info("action: close_connection | result: success")
        if not self._is_client_closed and self._current_peer is not None:
            self._is_client_closed = True
            self._current_peer.close()
            logging.info("action: close_connection | result: success")
        os._exit(0)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._keep_running:
            try:
                self._current_peer = self.__accept_new_connection()
                self.__handle_client_connection()
            except Exception as e:
                break

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        if self._current_peer is None:
            return 

        try:
            # TODO: Modify the receive to avoid short-reads
            msg = self._current_peer.recv(1024).rstrip().decode('utf-8')
            addr = self._current_peer.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # TODO: Modify the send to avoid short-writes
            self._current_peer.send("{}\n".format(msg).encode('utf-8'))#aqui se puede ejecutar el handler
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            if not self._is_client_closed:
                self._is_client_closed = True
                self._current_peer.close()
                logging.info("action: close_connection | result: success")

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
