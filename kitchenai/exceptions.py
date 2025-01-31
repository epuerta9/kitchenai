class NoRespondersError(Exception):
    """Exception raised when no NATS responders are available for a request."""
    
    def __init__(self, message="No responders available for request", details=None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message 