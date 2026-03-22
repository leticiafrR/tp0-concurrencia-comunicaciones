import os
import socket
import logging
import signal
from .server_protocol import ClientDisconnectedException, ServerProtocol
from typing import Optional
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

    def run(self):
        while self._keep_running and (len(self._client_protocols) < self._cant_clients):
            try:
                peer = self.__accept_new_connection()
                self.protocol = ServerProtocol(peer)#puede lanzar una excepción
                self._client_protocols[self.protocol.agency] = self.protocol
                logging.info(f"action: new_client_connected | result: success | agency: {self.protocol.agency} | total_clients: {len(self._client_protocols)} | max_clients: {self._cant_clients}")

            except Exception as e:
                logging.error(f"action: iteration | result: fail | error: {e}")
                break
        self.__process_all_bets()
        winners_by_agency = self.__define_winners()
        self.__spread_winners(winners_by_agency)

        
    def __process_all_bets(self):
        # logging.info("action: process_bets | result: in_progress")
        for clientID, protocol in list(self._client_protocols.items()):
            # logging.info(f"action: process_bet | result: in_progress | agency: {clientID}")
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
                logging.info(f"action: send_winners | result: success | agency: {agency} | amount: {len(winners)}")
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
                store_bets(bets)
                logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
                protocol.sendConfirmation(True)
            except ClientDisconnectedException as e:
                # debo apagar el cliente y eliminar del diccionario su protocolo
                protocol.shutdown()
                self._client_protocols.pop(agency, None)
                break


    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
