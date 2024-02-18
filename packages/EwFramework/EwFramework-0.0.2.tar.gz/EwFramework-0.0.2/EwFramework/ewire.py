class Calculator:
    """A simple calculator class."""

    def __init__(self):
        """Initialize the calculator."""
        pass

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def subtract(self, a, b):
        """Subtract one number from another."""
        return a - b

    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b

    def divide(self, a, b):
        """Divide one number by another."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b