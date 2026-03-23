from .serializer import deserializeInt, deserializeString, serializeBool, serializeWinners
from socket import socket
from .utils import Bet
from typing import List, Optional
from .constants import *

class ClientDisconnectedException(Exception):
    pass

class ServerProtocol:
    def __init__(self, conn: socket):
        self.__peer = conn
        self.__is_client_closed = False
        self.__expected_bets_current_batch: Optional[int] = None
        self.agency: str = ""
        self.meetClient()

    def meetClient(self):
        byte_agency = self.__receiveInt(U8_SIZE)
        self.agency = str(byte_agency)

    def sendConfirmation(self, flag: bool):
        f = serializeBool(flag)
        self.__sendBytes(f)

    def sendWinners(self, winners: List[str]):
        if len(winners) > 255:
            raise ValueError("too many winners for one agency")
        payload = serializeWinners(winners)
        self.__sendBytes(bytes(payload))

    def receiveBatch(self) -> List[Bet]:
        self.__expected_bets_current_batch = self.__receiveBatchSize()
        bets = []
        for _ in range(self.__expected_bets_current_batch):
            bet = self.__receiveBet()
            bets.append(bet)
        return bets
    
    def isEndOfTransmission(self) -> bool:
        end = (self.__receiveInt(U8_SIZE) == TYPE_END_OF_TRANSMISSION)
        return end
          
    def shutdown(self)->bool:
        if not self.__is_client_closed:
            self.__is_client_closed = True
            self.__peer.close()
            return True
        return False

    def __receiveBet(self) -> Bet:
        first_name=self.__receiveString()
        last_name=self.__receiveString()
        document=self.__receiveString()
        birthdate  = self.__receiveString()
        number=self.__receiveString()
        return Bet(
            agency=self.agency,
            first_name=first_name,
            last_name=last_name,
            document=document,
            birthdate=birthdate,
            number=number
        )
    
    def __receiveBatchSize(self) -> int:
        return deserializeInt(self.__receiveBytes(U8_SIZE))

    def __receiveBytes(self, nBytes: int) -> bytes:
        buf = bytearray(nBytes)
        totalRead = 0

        while totalRead < nBytes:
            seq = self.__peer.recv(nBytes - totalRead)
            if len(seq) == 0:
                raise ClientDisconnectedException()
            buf[totalRead:totalRead + len(seq)] = seq
            totalRead += len(seq)
        return bytes(buf)
    
    def __receiveInt(self, int_size: int) -> int:
        num = deserializeInt(self.__receiveBytes(int_size))
        return num

    def __receiveString(self) -> str:
        size = self.__receiveInt(U16_SIZE)
        return deserializeString(self.__receiveBytes(size))

    def __sendBytes(self, msg: bytes):
        msg_size = len(msg)
        bytesSent = 0
        while bytesSent < msg_size:
            sent = self.__peer.send(msg[bytesSent:])
            bytesSent += sent