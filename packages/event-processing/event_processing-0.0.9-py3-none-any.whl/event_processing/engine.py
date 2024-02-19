from threading import Thread
from queue import Queue


class Engine:
    def __init__(self):
        self.subscriptions = {}
        self.events = Queue()
        self.lock = False

    def subscribe(self, subscriber, topic):

        # If it is a new topic
        if topic not in self.subscriptions:
            self.subscriptions[topic] = {}

        # Save the listener callback
        self.subscriptions[topic][subscriber.id] = subscriber.receive
        subscriber._send = self.inject

    def unsubscribe(self, subscriber_id, topic):

        # If topic exists
        if topic in self.subscriptions:
            # If subscriber_id is a listener in the topic
            if subscriber_id in self.subscriptions[topic]:
                # Remove from the list
                del self.subscriptions[topic][subscriber_id]

    def inject(self, event):

        # Put event into the queue
        self.events.put(event)

        # If consume() is not running already
        if not self.lock:
            self.consume()

    # Single threaded because it is designed to be deterministic
    # It should only guarantee the order
    def consume(self):

        self.lock = True

        while not self.events.empty():

            event = self.events.get()

            # List all callbacks functions subscribed in event.topic
            if event.topic in self.subscriptions:
                for subscriber in self.subscriptions[event.topic]:
                    # Do not send event to itself
                    if event.sender != subscriber:
                        # Call the function
                        self.subscriptions[event.topic][subscriber](event)

        self.lock = False
