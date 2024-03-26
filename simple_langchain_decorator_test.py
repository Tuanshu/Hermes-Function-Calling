from langchain.tools import tool


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@tool(return_direct=False)
def calculator(number_1: int, number_2: int, operation: str) -> int | float:
    """
    Perform simple arithmetic operations between two integer values.

    Supported operations are addition (+), subtraction (-), multiplication (*), and division (/).

    Parameters:
    - number_1 (int): The first integer operand.
    - number_2 (int): The second integer operand.
    - operation (str): The arithmetic operation to be performed. Should be one of '+', '-', '*', '/'.

    Returns:
    int | float: The result of the arithmetic operation.

    Note: Division by zero will return 'NaN' (not a number).
    """

    try:
        if operation == '+':
            return number_1 + number_2
        elif operation == '-':
            return number_1 - number_2
        elif operation == '*':
            return number_1 * number_2
        elif operation == '/':
            if number_2 == 0:
                return float('nan')  # Return 'NaN' for division by zero
            return number_1 / number_2
        else:
            raise ValueError("Unsupported operation. Please use '+', '-', '*', or '/'.")
    except Exception as e:
        # Handle any unexpected errors
        return str(e)
    

if __name__=="__main__":
    calculator(1,2,'+')