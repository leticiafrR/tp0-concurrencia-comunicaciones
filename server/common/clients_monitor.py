import threading


class ClientsMonitor:
    def __init__(self):
        self._clients_lock = threading.Lock()
        self._clients = {}

    def number_of_clients_connected(self) -> int:
        with self._clients_lock:
            return len(self._clients) 
        
    def add_client(self, client):
        with self._clients_lock:
            self._clients[client.protocol.agency] = client
            
    def delete_client(self, agency: str):
        with self._clients_lock:
            self._clients.pop(agency, None)

    def stop_all_clients(self):
        """
        llama a shutdown a todos los clientes para que cierren sus conexiones y se joineen a sus threads
        """
        with self._clients_lock:
            clients = list(self._clients.values())
            self._clients.clear()

        for client in clients:
            client.shutdown()

    def spread_winners(self, winners_by_agency: dict[str, list[str]]):
        with self._clients_lock:
            clients = list(self._clients.items())

        for agency, client in clients:
            client.receive_winners(winners_by_agency.get(agency, []))