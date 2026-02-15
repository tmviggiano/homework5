from abc import ABC, abstractmethod
from app.operations import Operations


class Calculation(ABC):

    def __init__(self, a: float, b:float) -> None:
        self.a: float = a
        self.b: float = b


    def execute(self) -> float:

        pass # pragma: no cover

    def __str__(self) -> str:
        """
        Provides a user-friendly string representation of the Calculation instance, 
        showing the operation name, operands, and result. This enhances **Readability** 
        and **Debugging** by giving a clear output for each calculation.

        **Returns:**
        - `str`: A string describing the calculation and its result.
        """
        result = self.execute()  # Run the calculation to get the result.
        operation_name = self.__class__.__name__.replace('Calculation', '')  # Derive operation name.
        return f"{self.__class__.__name__}: {self.a} {operation_name} {self.b} = {result}"

    def __repr__(self) -> str:
        """
        Provides a technical, unambiguous representation of the Calculation instance 
        showing the class name and operand values. This is useful for debugging 
        since it gives a clear and consistent format for all Calculation objects.

        **Returns:**
        - `str`: A string containing the class name and operands.
        """
        return f"{self.__class__.__name__}(a={self.a}, b={self.b})"
    

class CalculationFactory:

    _calculations = {}

    @classmethod
    def register_calculation(cls, calculation_type: str):
        """
        This method is a decorator used to register a specific Calculation subclass 
        under a unique calculation type. Registering classes with string identifiers 
        like "add" or "multiply" enables easy access to different operations 
        dynamically at runtime.

        **Parameters:**
        - `calculation_type (str)`: A short identifier for the type of calculation 
          (e.g., 'add' for addition).
        
        **Benefits of Using a Decorator for Registration:**
        - **Modularity**: By using a decorator, we can easily add new calculations by 
          annotating new subclasses with `@CalculationFactory.register_calculation`.
        - **Dynamic Binding**: This approach binds each calculation type to a class dynamically, 
          allowing us to extend our application without altering the core logic.
        """
        def decorator(subclass):
            # Convert calculation_type to lowercase to ensure consistency.
            calculation_type_lower = calculation_type.lower()
            # Check if the calculation type has already been registered to avoid duplication.
            if calculation_type_lower in cls._calculations:
                raise ValueError(f"Calculation type '{calculation_type}' is already registered.")
            # Register the subclass in the _calculations dictionary.
            cls._calculations[calculation_type_lower] = subclass
            return subclass  # Return the subclass for chaining or additional use.
        return decorator  # Return the decorator function.
    
    @classmethod
    def create_calculation(cls, calculation_type: str, a: float, b: float) -> Calculation:
        """
        Factory method that creates instances of Calculation subclasses based on 
        a specified calculation type.

        **Parameters:**
        - `calculation_type (str)`: The type of calculation ('add', 'subtract', 'multiply', 'divide').
        - `a (float)`: The first operand.
        - `b (float)`: The second operand.
        
        **Returns:**
        - `Calculation`: An instance of the appropriate Calculation subclass.

        **How Does This Help?**
        - By centralizing object creation here, we only need to specify calculation types 
          as strings, making it easy to choose different calculations dynamically. 
        - **Error Handling**: If the specified type is not available, we provide a 
          clear error message listing valid options, helping prevent errors and 
          ensuring the user knows the supported types.
        """
        calculation_type_lower = calculation_type.lower()
        calculation_class = cls._calculations.get(calculation_type_lower)
        # If the type is unsupported, raise an error with the available types.
        if not calculation_class:
            available_types = ', '.join(cls._calculations.keys())
            raise ValueError(f"Unsupported calculation type: '{calculation_type}'. Available types: {available_types}")
        # Create and return an instance of the requested calculation class with the provided operands.
        return calculation_class(a, b)
    

@CalculationFactory.register_calculation('add')
class AddCalculation(Calculation):
    """
    AddCalculation represents an addition operation between two numbers.
    
    **Why Create Separate Classes for Each Operation?**
    - **Polymorphism**: Each calculation type can be used interchangeably through the `execute` method.
    - **Modularity**: Encapsulating each operation in a separate class makes it easy to 
      modify, test, or extend without affecting other calculations.
    - **Clear Responsibility**: Each class has a clear, single purpose, making the code easier to read.
    """

    def execute(self) -> float:
        # Calls the addition method from the Operation module to perform the addition.
        return Operations.addition(self.a, self.b)


@CalculationFactory.register_calculation('subtract')
class SubtractCalculation(Calculation):
    """
    SubtractCalculation represents a subtraction operation between two numbers.
    
    **Implementation Note**: This class specifically handles subtraction, keeping 
    the implementation separate from other operations.
    """

    def execute(self) -> float:
        # Calls the subtraction method from the Operation module to perform the subtraction.
        return Operations.subtraction(self.a, self.b)


@CalculationFactory.register_calculation('multiply')
class MultiplyCalculation(Calculation):
    """
    MultiplyCalculation represents a multiplication operation.
    
    By encapsulating the multiplication logic here, we achieve a clear separation of 
    concerns, making it easy to adjust the multiplication logic without affecting other calculations.
    """

    def execute(self) -> float:
        # Calls the multiplication method from the Operation module to perform the multiplication.
        return Operations.multiplication(self.a, self.b)


@CalculationFactory.register_calculation('divide')
class DivideCalculation(Calculation):
    """
    DivideCalculation represents a division operation.
    
    **Special Case - Division by Zero**: Division requires extra error handling to 
    prevent dividing by zero, which would cause an error in the program. This class 
    checks if the second operand is zero before performing the operation.
    """

    def execute(self) -> float:
        # Before performing division, check if `b` is zero to avoid ZeroDivisionError.
        if self.b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        # Calls the division method from the Operation module to perform the division.
        return Operations.division(self.a, self.b)
    

@CalculationFactory.register_calculation('power')
class PowerCalculation(Calculation):
    def execute(self):
        return Operations.power(self.a, self.b)