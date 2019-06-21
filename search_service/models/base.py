from abc import ABCMeta, abstractmethod


class Base(metaclass=ABCMeta):
    """
    A base class for ES model
    """

    @abstractmethod
    def get_attrs(cls):
        # return a set of attributes for the class
        ...
