import threading

lock = threading.Lock()


class LineNumber:
    def __init__(self):
        self.index = 0

    def add(self):
        lock.acquire()
        try:
            self.index += 1
        finally:
            lock.release()

    def get(self):
        lock.acquire()
        try:
            return self.index
        finally:
            lock.release()
