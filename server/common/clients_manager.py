from .client import Client
from socket import socket
from .bets_store_monitor import BetsStoreMonitor
from .clients_monitor import ClientsMonitor
from threading import Event, Barrier, BrokenBarrierError

class ClientsManager:
    def __init__(self, cant_clients: int,shutdown_event: Event, all_bets_received_barrier: Barrier):
        self._cant_clients = cant_clients
        self._bets_store_monitor = BetsStoreMonitor()
        self._clients_monitor = ClientsMonitor()
        self._shutdown_event = shutdown_event
        self._all_bets_received_barrier = all_bets_received_barrier


    def are_all_clients_connected(self) -> bool:
        return  self._clients_monitor.number_of_clients_connected() == self._cant_clients
    
    def add_client(self, peer: socket):
        """
        crea el cliente y lo agrega con el monitor de clientes y guarda el extremo de lectura de la queue para poder comunicarse con los clientes
        """
        
        client = Client(
            peer,
            self._shutdown_event,
            self._bets_store_monitor,
            self._clients_monitor,
            self._all_bets_received_barrier
        )
        self._clients_monitor.add_client(client)
    
    def stopClients(self):
        self._shutdown_event.set()
        self._clients_monitor.stop_all_clients()
        try:
            self._all_bets_received_barrier.abort()
        except BrokenBarrierError:
            pass

    def join_all_clients(self):
        self._clients_monitor.join_all_clients()
        
    def wait_for_storing_all_bets(self):
        self._all_bets_received_barrier.wait()

    def spread_winners(self, winners_by_agency: dict[str, list[str]]):
        self._clients_monitor.spread_winners(winners_by_agency)

