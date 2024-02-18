
def calculator(a: float, b: float, operation: str) -> float:
    if operation == '+':
        return a + b
    elif operation == '-':
        return a - b
    elif operation == '*':
        return a * b
    elif operation == '/':
        return a / b
    else:
        raise ValueError(f"Not supported operation {operation}")