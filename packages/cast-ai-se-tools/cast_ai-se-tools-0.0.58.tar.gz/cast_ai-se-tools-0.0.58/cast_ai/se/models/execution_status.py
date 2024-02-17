class ExecutionStatus:
    def __init__(self, error_message: str = ""):
        self.success = not error_message
        self.error_message = error_message
