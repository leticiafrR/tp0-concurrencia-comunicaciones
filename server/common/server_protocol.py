from dataclasses import dataclass
import re
from serializer import deserializeInt, deserializeString, serializeBool
from socket import socket
from utils import Bet

class ServerProtocol:
    def __init__(self, conn: socket):
        self.__peer = conn
        self.__is_client_closed = False

    def receiveBet(self) -> Bet:
        return Bet( agency="2",
            first_name=self.__receiveString(),
                    last_name=self.__receiveString(),
                    document=str(self.__receiveInt(4)),
                    birthdate=str(self.__receiveInt(2))+'-'+str(self.__receiveInt(1))+'-'+str(self.__receiveInt(1)),
                    number=str(self.__receiveInt(2))
            )

    def sendConfirmation(self, flag: bool):
        f = serializeBool(flag)
        self.__sendBytes(f)
      
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
            seq = self.__peer.recv(nBytes)
            totalRead += len(seq)
        return bytes(buf)
    
    def __receiveString(self) -> str:
        size = deserializeInt(self.__receiveBytes(2))
        return deserializeString(self.__receiveBytes(size))

    def __receiveInt(self, cantBytes: int) -> int:
        return deserializeInt(self.__receiveBytes(cantBytes))

    def __sendBytes(self, msg: bytes):
        msg_size = len(msg)
        bytesSent = 0
        while bytesSent < msg_size:
            sent = self.__peer.send(msg[bytesSent:])
            bytesSent += sent