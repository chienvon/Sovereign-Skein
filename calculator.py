#!/usr/bin/env python3
"""
Simple Python Calculator
Author: Ego Worker (AI Agent)
"""

import re
from typing import Union

class Calculator:
    """Simple calculator with basic operations."""
    
    def __init__(self):
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"{a} × {b} = {result}")
        return result
    
    def divide(self, a: float, b: float) -> Union[float, str]:
        """Divide a by b."""
        if b == 0:
            return "Error: Division by zero"
        result = a / b
        self.history.append(f"{a} ÷ {b} = {result}")
        return result
    
    def power(self, a: float, b: float) -> float:
        """Raise a to the power of b."""
        result = a ** b
        self.history.append(f"{a} ^ {b} = {result}")
        return result
    
    def modulo(self, a: float, b: float) -> Union[float, str]:
        """Calculate a modulo b."""
        if b == 0:
            return "Error: Division by zero"
        result = a % b
        self.history.append(f"{a} % {b} = {result}")
        return result
    
    def clear_history(self):
        """Clear calculation history."""
        self.history = []
    
    def get_history(self) -> list:
        """Get calculation history."""
        return self.history
    
    def evaluate_expression(self, expression: str) -> Union[float, str]:
        """Evaluate a mathematical expression string."""
        try:
            # Remove spaces and validate
            expr = expression.replace(" ", "")
            
            # Only allow numbers and basic operators
            if not re.match(r'^[0-9+\-*/.()%^]+$', expr):
                return "Error: Invalid characters in expression"
            
            # Evaluate safely
            result = eval(expr)
            self.history.append(f"{expression} = {result}")
            return result
        except Exception as e:
            return f"Error: {str(e)}"


def main():
    """Main function to run the calculator."""
    calc = Calculator()
    
    print("🧮 Simple Python Calculator")
    print("=" * 40)
    print("Operations: +, -, *, /, **, %")
    print("Commands: 'history', 'clear', 'quit'")
    print("=" * 40)
    
    while True:
        user_input = input("\nEnter expression or command: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'history':
            if calc.history:
                print("\nCalculation History:")
                for entry in calc.history:
                    print(f"  {entry}")
            else:
                print("No history yet.")
        elif user_input.lower() == 'clear':
            calc.clear_history()
            print("History cleared.")
        else:
            result = calc.evaluate_expression(user_input)
            print(f"Result: {result}")


if __name__ == "__main__":
    main()
