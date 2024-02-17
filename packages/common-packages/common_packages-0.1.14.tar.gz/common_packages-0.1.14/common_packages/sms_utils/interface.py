from abc import ABCMeta, abstractmethod


class SendSms(metaclass=ABCMeta):
    @abstractmethod
    def send(self, content):
        ...
