class QueryHandlerBadRequestError(Exception):
    """Raised when a query handler encounters a bad request"""
    def __init__(self, message="Bad request from query handler"):
        self.message = message
        super().__init__(self.message)
