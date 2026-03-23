from .bets_store_monitor import BetsStoreMonitor

from .server_protocol import ServerProtocol, ClientDisconnectedException
import threading
from queue import Queue
from socket import socket
from threading import Event, Barrier,BrokenBarrierError
import logging
"""
Todos los recursos asociados a un cliente (socket, thread, queue) se encuentran en esta clase.
tiene el accesos al monitor de clientes para eliminarse a si mismo cuando se desconecta.
"""
class Client:
    def __init__(self,
                peer: socket,
                shutdown_event: Event,
                bets_stores_monitor: BetsStoreMonitor,
                clients_monitor,
                all_bets_received_barrier: Barrier
                ):
        self.protocol : ServerProtocol = ServerProtocol(peer)
        self.agency : str = self.protocol.agency
        self.winners_queue : Queue = Queue(maxsize=1)
        self.shutdown_event : Event = shutdown_event
        self.bets_stores_monitor : BetsStoreMonitor = bets_stores_monitor
        self.thread = threading.Thread(
                    target=self.__process_bets_from_client,
                    args=(self.protocol.agency, clients_monitor, all_bets_received_barrier),
                    daemon=True,
                )
        self.thread.start()

    def shutdown(self):
        self.protocol.shutdown()
        self.thread.join(timeout=2)

    def __keep_running(self) -> bool:
        return not self.shutdown_event.is_set()
    
    def __abort_barrier_waiting(self, all_bets_received_barrier: Barrier):
        try:
            all_bets_received_barrier.abort()
        except BrokenBarrierError:
            pass

    def receive_winners(self, winners :list[str]):
        self.winners_queue.put(winners)

    def __process_bets_from_client(self, agency: str, clients_monitor, all_bets_received_barrier: Barrier):
        end_of_transmission_received = False
        while not end_of_transmission_received:
            try:
                if not self.__keep_running():
                    return

                if self.protocol.isEndOfTransmission():
                    end_of_transmission_received = True
                    break

                bets = self.protocol.receiveBatch()
                self.bets_stores_monitor.store(bets)
                self.protocol.sendConfirmation(True)
            except ClientDisconnectedException:
                self.protocol.shutdown()
                clients_monitor.delete_client(agency)
                self.__abort_barrier_waiting(all_bets_received_barrier)
                return
            except Exception as e:
                logging.error(f"action: process_bets | result: fail | agency: {agency} | error: {e}")
                self.protocol.shutdown()
                clients_monitor.delete_client(agency)
                self.__abort_barrier_waiting(all_bets_received_barrier)
                return

        try:
            all_bets_received_barrier.wait()
        except BrokenBarrierError:
            return

        winners = self.winners_queue.get()
        try:
            self.protocol.sendWinners(winners)
            logging.debug(f"action: send_winners | result: success | agency: {agency} | amount: {len(winners)}")
        except Exception as e:
            logging.error(f"action: send_winners | result: fail | agency: {agency} | error: {e}")
