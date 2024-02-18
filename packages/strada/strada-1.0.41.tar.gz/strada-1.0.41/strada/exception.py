class StradaValidationException(Exception):
    """Custom exception class for Strada validation errors."""

    def __init__(self, message, schema=None, data=None):
        self.schema = schema
        self.data = data
        super().__init__(message)

    def __str__(self):
        return f"{super().__str__()} - Schema: {self.schema}, Data: {self.data}"
