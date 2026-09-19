def calculate(a: float, b: float, operation: str) -> float:
    if operation == "add":
        return a + b

    elif operation == "subtract":
        return a - b

    elif operation == "multiply":
        return a * b

    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    else:
        raise ValueError(f"Unsupported operation: {operation}")


def count_words(text: str) -> int:
    """Count the number of words in a piece of text."""
    return len(text.split())


TOOL_REGISTRY = {
    "calculate": calculate,
    "count_words": count_words,
}
