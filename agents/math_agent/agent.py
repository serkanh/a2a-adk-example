"""Math Agent - Headless A2A service for mathematical operations."""

import os

from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a


def add_numbers(a: float, b: float) -> dict:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Dictionary with the sum result
    """
    return {"result": a + b, "operation": "addition"}


def multiply_numbers(a: float, b: float) -> dict:
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Dictionary with the product result
    """
    return {"result": a * b, "operation": "multiplication"}


def check_prime(n: int) -> dict:
    """Check if a number is prime.

    Args:
        n: The number to check

    Returns:
        Dictionary indicating if the number is prime
    """
    if n < 2:
        return {"number": n, "is_prime": False, "reason": "Numbers less than 2 are not prime"}
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return {"number": n, "is_prime": False, "reason": f"Divisible by {i}"}
    return {"number": n, "is_prime": True, "reason": "No divisors found"}


root_agent = Agent(
    model="gemini-2.0-flash",
    name="math_agent",
    description="Agent specialized in mathematical operations including addition, multiplication, and prime number checking.",
    instruction="""You are a mathematical assistant.
    Use the provided tools to perform calculations accurately.
    Always show your work and explain the results clearly.""",
    tools=[add_numbers, multiply_numbers, check_prime],
)

# Create A2A-compatible app
PORT = int(os.environ.get("PORT", 8001))
a2a_app = to_a2a(root_agent, port=PORT)
