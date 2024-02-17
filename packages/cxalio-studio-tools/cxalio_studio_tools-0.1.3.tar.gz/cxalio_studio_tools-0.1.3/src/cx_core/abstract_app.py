from abc import ABCMeta, abstractmethod


class AbstractApp(metaclass=ABCMeta):
    @abstractmethod
    def run(self):
        pass



