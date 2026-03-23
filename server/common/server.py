import os
import socket
import logging
import signal
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
        self.__register_signal_handlers()

    def run(self):
        while self._keep_running and (len(self._client_protocols) < self._cant_clients):
            try:
                peer, addr = self._server_socket.accept()
                logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
                protocol = ServerProtocol(peer)#puede lanzar una excepción
                self._client_protocols[protocol.agency] = protocol
            except Exception as _:
                logging.error(f'action: accept_connections | result: fail | ip: {addr[0]}')
                break
        self.__process_all_bets()
        winners_by_agency = self.__define_winners()
        self.__spread_winners(winners_by_agency)

        
    def __process_all_bets(self):
        for clientID, protocol in list(self._client_protocols.items()):
            self.__process_bets_from_client(protocol, clientID)

    
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
        for agency, protocol in self._client_protocols.items():
            winners = winners_by_agency.get(agency, [])
            try:
                protocol.sendWinners(winners)
                logging.debug(f"action: send_winners | result: success | agency: {agency} | amount: {len(winners)}")
            except Exception as e:
                logging.error(f"action: send_winners | result: fail | agency: {agency} | error: {e}")


    def __process_bets_from_client(self, protocol: ServerProtocol,agency: str):
        end_of_transmission_received = False
        while not end_of_transmission_received:
            try:
                if protocol.isEndOfTransmission():
                    end_of_transmission_received = True
                    break
                bets = protocol.receiveBatch()
                self.__store_bets(bets)
                protocol.sendConfirmation(True)
            except ClientDisconnectedException as e:
                protocol.shutdown()
                self._client_protocols.pop(agency, None)
                break

    def __store_bets(self, bets):
        store_bets(bets)
        logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")

    def __register_signal_handlers(self):
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        self._keep_running = False
        self._server_socket.close()
        logging.info("action: close_connection | result: success")
        for protocol in self._client_protocols.values():
            protocol.shutdown()
            logging.info("action: close_connection | result: success")
        os._exit(0)