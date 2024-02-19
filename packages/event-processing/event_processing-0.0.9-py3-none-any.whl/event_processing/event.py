from datetime import datetime

class Event:

    from datetime import datetime

    def __init__(self, topic, partition, value, timestamp=datetime.now()):

        self.sender = 0
        self.timestamp = timestamp
        self.topic = topic
        self.partition = partition
        self.value = value

    def __repr__(self):
        return '{} - {}/{}: {}'.format(self.timestamp, self.topic, self.partition, self.value)