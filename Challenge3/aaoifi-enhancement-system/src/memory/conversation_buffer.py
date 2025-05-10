from collections import deque

class ConversationBuffer:
    def __init__(self, max_size=100):
        self.buffer = deque(maxlen=max_size)

    def add_message(self, sender, message):
        self.buffer.append({"sender": sender, "message": message})

    def get_messages(self):
        return list(self.buffer)

    def get_messages_by_sender(self, sender):
        return [msg for msg in self.buffer if msg["sender"] == sender]

    def clear(self):
        self.buffer.clear()