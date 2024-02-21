from threading import Thread, Lock
from typing import Callable


class ReceiveEngine(Thread):
    def __init__(self, receiver:Callable, handler:Callable):
        super().__init__()
        self.is_launch = False
        self.handler = handler
        self.receiver = receiver

    def run(self):
        """
        This function is used to run the finite state machine to detect the gesture.
        """
        self.is_launch = True
        while self.is_launch:
            status, data = self.receiver()
            if status.value == 0:
                self.handler(data)

    def stop(self):
        '''self.is_launch 要 False 才會停止接收資料
        修改 self.is_launch 要lock
        '''
        if self.is_alive:
            with Lock():
                self.is_launch = False
            self.join()
            print('Engine stopped')
        pass