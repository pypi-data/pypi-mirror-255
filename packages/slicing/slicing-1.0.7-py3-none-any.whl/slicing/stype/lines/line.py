import abc


class Line(abc.ABC):

    @abc.abstractmethod
    def match(self, line): ...

    @abc.abstractmethod
    def accept(self, slicer): ...
