from .serializer import deserializeInt, deserializeString, serializeBool
from socket import socket
from .utils import Bet
from typing import List, Optional
AGENCY_EXAMPLE = "1"
U16_SIZE = 2

class ClientDisconnectedException(Exception):
    pass

class ServerProtocol:
    def __init__(self, conn: socket):
        self.__peer = conn
        self.__is_client_closed = False
        self.__expected_bets_current_batch: Optional[int] = None

    def sendConfirmation(self, flag: bool):
        f = serializeBool(flag)
        self.__sendBytes(f)

    def receiveBatch(self) -> List[Bet]:
        self.__expected_bets_current_batch = self.__receiveBatchSize()
        bets = []
        for _ in range(self.__expected_bets_current_batch):
            bet = self.__receiveBet()
            bets.append(bet)
        return bets

    def __receiveBet(self) -> Bet:
        first_name=self.__receiveString()
        last_name=self.__receiveString()
        document=self.__receiveString()
        birthdate  = self.__receiveString()
        number=self.__receiveString()
        return Bet(
            agency=AGENCY_EXAMPLE,
            first_name=first_name,
            last_name=last_name,
            document=document,
            birthdate=birthdate,
            number=number
        )
    
    def __receiveBatchSize(self) -> int:
        return deserializeInt(self.__receiveBytes(U16_SIZE))

      
    def shutdown(self)->bool:
        if not self.__is_client_closed:
            self.__is_client_closed = True
            self.__peer.close()
            return True
        return False

    def __receiveBytes(self, nBytes: int) -> bytes:
        buf = bytearray(nBytes)
        totalRead = 0

        while totalRead < nBytes:
            seq = self.__peer.recv(nBytes - totalRead)
            if len(seq) == 0:
                raise ClientDisconnectedException("client closed connection")
            buf[totalRead:totalRead + len(seq)] = seq
            totalRead += len(seq)
        return bytes(buf)
    
    def __receiveString(self) -> str:
        size = deserializeInt(self.__receiveBytes(U16_SIZE))
        return deserializeString(self.__receiveBytes(size))

    def __sendBytes(self, msg: bytes):
        msg_size = len(msg)
        bytesSent = 0
        while bytesSent < msg_size:
            sent = self.__peer.send(msg[bytesSent:])
            bytesSent += sent