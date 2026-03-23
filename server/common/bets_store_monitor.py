import logging
import threading
from .utils import Bet, store_bets


class BetsStoreMonitor:
    def __init__(self):
        self._lock = threading.Lock()

    def store(self, bets: list[Bet]) -> None:
        with self._lock:
            store_bets(bets)
        logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
