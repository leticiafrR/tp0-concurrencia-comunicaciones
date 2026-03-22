import os
import socket
import logging
import signal
import threading
import queue
from .server_protocol import ClientDisconnectedException, ServerProtocol
from .utils import store_bets, load_bets, has_won

class Server:
    def __init__(self, port, listen_backlog, cant_clients):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._keep_running = True
        self._cant_clients = cant_clients
        self._client_protocols = {}
        self._client_threads = []
        self._winners_queues = {}
        self._clients_lock = threading.Lock()
        self._store_lock = threading.Lock()
        self._threads_barrier = threading.Barrier(self._cant_clients + 1)
        self._shutdown_event = threading.Event()
        self.__register_signal_handlers()


    def __register_signal_handlers(self):
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        self._keep_running = False
        self._shutdown_event.set()
        try:
            self._server_socket.close()
        except OSError:
            pass

        try:
            self._threads_barrier.abort()
        except threading.BrokenBarrierError:
            pass

        logging.info("action: close_connection | result: success")

        with self._clients_lock:
            protocols = list(self._client_protocols.values())

        for protocol in protocols:
            protocol.shutdown()
            logging.info("action: close_connection | result: success")

        for client_thread in self._client_threads:
            client_thread.join(timeout=1)

        if signum is not None:
            os._exit(0)

    def run(self):
        while self._keep_running:
            with self._clients_lock:
                if len(self._client_protocols) >= self._cant_clients:
                    break

            addr = ("unknown", 0)
            try:
                peer, addr = self._server_socket.accept()
                logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')

                protocol = ServerProtocol(peer)
                winners_queue = queue.Queue(maxsize=1)

                with self._clients_lock:
                    self._client_protocols[protocol.agency] = protocol
                    self._winners_queues[protocol.agency] = winners_queue

                client_thread = threading.Thread(
                    target=self.__process_bets_from_client,
                    args=(protocol, protocol.agency, winners_queue),
                    daemon=True,
                )
                self._client_threads.append(client_thread)
                client_thread.start()
            except Exception as _:
                if not self._keep_running:
                    break
                logging.error(f'action: accept_connections | result: fail | ip: {addr[0]}')
                break

        if len(self._client_threads) != self._cant_clients:
            try:
                self._threads_barrier.abort()
            except threading.BrokenBarrierError:
                pass
            for client_thread in self._client_threads:
                client_thread.join()
            return

        try:
            self._threads_barrier.wait()
        except threading.BrokenBarrierError:
            for client_thread in self._client_threads:
                client_thread.join()
            return

        winners_by_agency = self.__define_winners()
        self.__spread_winners(winners_by_agency)

        for client_thread in self._client_threads:
            client_thread.join()

    
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


    def __spread_winners(self, winners_by_agency):
        with self._clients_lock:
            winners_queues = dict(self._winners_queues)

        for agency, winners_queue in winners_queues.items():
            winners = winners_by_agency.get(agency, [])
            winners_queue.put(winners)


    def __process_bets_from_client(self, protocol: ServerProtocol, agency: str, winners_queue: queue.Queue):
        end_of_transmission_received = False
        while not end_of_transmission_received:
            try:
                if self._shutdown_event.is_set():
                    return

                if protocol.isEndOfTransmission():
                    end_of_transmission_received = True
                    break

                bets = protocol.receiveBatch()
                self.__store_bets(bets)
                protocol.sendConfirmation(True)
            except ClientDisconnectedException:
                protocol.shutdown()
                with self._clients_lock:
                    self._client_protocols.pop(agency, None)
                    self._winners_queues.pop(agency, None)
                try:
                    self._threads_barrier.abort()
                except threading.BrokenBarrierError:
                    pass
                return

        try:
            self._threads_barrier.wait()
        except threading.BrokenBarrierError:
            return

        winners = winners_queue.get()
        try:
            protocol.sendWinners(winners)
            logging.debug(f"action: send_winners | result: success | agency: {agency} | amount: {len(winners)}")
        except Exception as e:
            logging.error(f"action: send_winners | result: fail | agency: {agency} | error: {e}")

    def __store_bets(self, bets):
        with self._store_lock:
            store_bets(bets)
        logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
   