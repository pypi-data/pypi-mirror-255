# --------------------------------------------
import asyncio
from abc import ABCMeta, abstractmethod
from itertools import groupby
from operator import attrgetter
from typing import List

class AbstractSubscriber(metaclass=ABCMeta):
    def __init__(self, priority: int = 0) -> None:
        """ Subscriber with priority.
        The lower the priority value, the higher the priority.
        When the publisher notifies the subscriber, 
        the subscribers with the highest priority will be notified first.
        """
        self.priority = priority

    @abstractmethod
    def subscribe(self, *args, **kwargs):
        pass


class AbstractPublisher(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs) -> None:
        self.subscribers: List[AbstractSubscriber] = []

    def register(self, subscriber: AbstractSubscriber):
        self.subscribers.append(subscriber)

    def unregister(self, subscriber: AbstractSubscriber):
        self.subscribers.remove(subscriber)

    @abstractmethod
    def update(self, *args, **kwargs):
        pass
    
    def notify(self, *args, **kwargs):
        pass 
        

class AsyncAbstractPublisher(AbstractPublisher):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
    @abstractmethod
    async def update(self, *args, **kwargs):
        pass

    async def notify(self, *args, **kwargs):
        results = []
        for _, subscribers in groupby(sorted(self.subscribers,
                                             key=attrgetter('priority')),
                                      key=attrgetter('priority')):
            tasks = [
                subscriber.subscribe(*args, **kwargs)
                for subscriber in subscribers
            ]
            results.append(await asyncio.gather(*tasks))
        return results