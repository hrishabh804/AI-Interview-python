import datetime

class ProctoringLogger:
    def log(self, message):
        timestamp = datetime.datetime.now().isoformat()
        print(f"[PROCTORING LOG] {timestamp}: {message}")

class ProctoringSystem:
    def __init__(self, logger):
        self.logger = logger

    def start(self):
        self.logger.log("Proctoring session started.")

    def stop(self):
        self.logger.log("Proctoring session stopped.")

    def log_event(self, event):
        self.logger.log(f"Event: {event}")
