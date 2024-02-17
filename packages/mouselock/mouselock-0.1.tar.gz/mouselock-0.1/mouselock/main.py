from pynput.mouse import Controller
from threading import Thread
from time import sleep


class Lock:

    __locked = False
    __mouse = Controller()

    def __lock(self, tick_delay, position):
        while self.__locked:
            self.__mouse.position = position
            sleep(tick_delay)

    def lock(self, tick_delay: float, position: tuple[int, int]):
        if not type(tick_delay) == float and not type(tick_delay) == int:
            raise TypeError("Argument <tick_delay> is not a float!")
        if not type(position) == tuple:
            raise TypeError("Argument <position> is not a tuple!")
        if not type(position[0]) == int:
            raise TypeError("Argument <position[0]> is not an int!")
        if not type(position[1]) == int:
            raise TypeError("Argument <position[1]> is not an int!")
        self.__locked = True
        Thread(target=self.__lock, args=(tick_delay, position)).start()

    def unlock(self): self.__locked = False