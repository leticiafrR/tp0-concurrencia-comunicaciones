import os
import socket
import logging
import signal
import threading

from .clients_manager import ClientsManager
from .utils import load_bets, has_won

class Server:
    def __init__(self, port, listen_backlog, cant_clients):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._keep_running = True
        self._cant_clients = cant_clients
        self._threads_barrier = threading.Barrier(self._cant_clients + 1)
        self._shutdown_event = threading.Event()
        self.__register_signal_handlers()
        self._clients_manager = ClientsManager(cant_clients, self._shutdown_event,self._threads_barrier)

    def __register_signal_handlers(self):
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        self._keep_running = False
        self._clients_manager.stopClients()
        try:
            self._server_socket.close()
        except OSError:
            pass
        logging.info("action: close_connection | result: success")
        if signum is not None:
            os._exit(0)

    def receive_clients(self):
        while self._keep_running and not self._clients_manager.are_all_clients_connected():
            try:
                peer, addr = self._server_socket.accept()
                logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
                self._clients_manager.add_client(peer)
            except OSError:
                if self._keep_running:
                    logging.error('action: accept_connections | result: fail | reason: socket_closed')
                break
            except Exception as _:
                logging.error('action: accept_connections | result: fail')
                self.shutdown(None, None)
                break

    def run(self):
        self.receive_clients()

        if not self._keep_running:
            return

        if not self._clients_manager.are_all_clients_connected():
            self._clients_manager.stopClients()
            return

        try:
            self._clients_manager.wait_for_storing_all_bets()
        except threading.BrokenBarrierError:
            self._clients_manager.stopClients()
            return
        winners_by_agency = self.__define_winners()
        self._clients_manager.spread_winners(winners_by_agency)
        self._clients_manager.stopClients()
  
    def __define_winners(self):
        winners_by_agency = {}
        for bet in load_bets():
            if not has_won(bet):
                continue
            agency = str(bet.agency)
            if agency not in winners_by_agency:
                winners_by_agency[agency] = []

            winners_by_agency[agency].append(bet.document)
        return winners_by_agency
