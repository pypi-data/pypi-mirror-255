import threading
import sys
import time


class BusyIndicator:
    _cancelation_token = False
    _thread = None

    def __init__(self, enabled:bool=True):
        self._enabled = enabled

    def __enter__(self):
        if not self._enabled:
            return

        self._thread = threading.Thread(target=BusyIndicator._worker, args=[lambda: self._cancelation_token])
        self._thread.start()

    @staticmethod
    def _worker(cancelation_token):
        symbols = ['-', '/', '|', '\\', '-']
        idx = 0
        start_time = time.time()

        time.sleep(0.2)

        while not cancelation_token():
            elapsed = time.time() - start_time
            if elapsed > 1.5:
                sys.stdout.write(f"\r   {symbols[idx]} {elapsed:.1f}sec")
            else:
                sys.stdout.write(f"\r   {symbols[idx]}")
            idx += 1
            if idx >= len(symbols):
                idx = 0
            time.sleep(0.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cancelation_token = True
