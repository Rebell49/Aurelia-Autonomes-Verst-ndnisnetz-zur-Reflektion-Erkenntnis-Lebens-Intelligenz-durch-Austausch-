class ThoughtStream:
    def __init__(self):
        self.thoughts = []

    def update(self):
        if len(self.thoughts) < 10:
            self.thoughts.append("Neuer Gedanke flieÃŸt...")

    def get_recent_thoughts(self):
        return self.thoughts[-10:]
