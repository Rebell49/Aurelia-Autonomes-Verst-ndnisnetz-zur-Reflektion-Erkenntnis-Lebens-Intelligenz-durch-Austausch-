import os
import json
import datetime

class ArchiveManager:
    def __init__(self, path):
        self.path = path
        self.thoughts_file = os.path.join(self.path, "gedanken.json")
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if not os.path.exists(self.thoughts_file):
            with open(self.thoughts_file, "w") as f:
                json.dump([], f)

    def save_thought(self, thought_text):
        with open(self.thoughts_file, "r") as f:
            data = json.load(f)
        data.append({"text": thought_text, "timestamp": str(datetime.datetime.now())})
        with open(self.thoughts_file, "w") as f:
            json.dump(data, f, indent=2)
