import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import MagicMock, Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory
from app.calculator_memento import CalculatorMemento

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

# Test Adding and Removing Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

# Test Performing Operations

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# Test Undo/Redo Functionality

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    # Mock CSV data to match the expected format in from_dict
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    # Test the load_history functionality
    try:
        calculator.load_history()
        # Verify history length after loading
        assert len(calculator.history) == 1
        # Verify the loaded values
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")
        
            
# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# Test REPL Commands (using patches for input/output handling)

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit_error(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history', side_effect=Exception) as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")

@patch('builtins.input', side_effect=['add', '2', '3','history', 'exit'])
@patch('builtins.print')
def test_calculator_repl_history_positive(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nCalculation History:")
@patch('builtins.input', side_effect=['history', 'exit'])
@patch('builtins.print')
def test_calculator_repl_history_negative(mock_print, mock_input):
    with patch('app.calculator.Calculator.show_history') as mock_history:
        mock_history.return_value = None
        calculator_repl()
        mock_history.assert_called_once()
        mock_print.assert_any_call("No calculations in history")

@patch('builtins.input', side_effect=['clear', 'exit'])
@patch('builtins.print')
def test_calculator_repl_clear(mock_print, mock_input):
    with patch('app.calculator.Calculator.clear_history') as mock_history:
        calculator_repl()
        mock_history.assert_called_once()
        mock_print.assert_any_call("History cleared")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")


def test_history_load_failure(calculator):
    # Patch load_history to simulate failure
    with patch.object(Calculator, 'load_history', side_effect=OperationError("Failed to load history")):
        # Since __init__ calls load_history, it will log a warning but not raise
        calc = Calculator(config=calculator.config)
        
        # Calling load_history directly should raise OperationError
        with pytest.raises(OperationError) as exc_info:
            calc.load_history()
        assert "Failed to load history" in str(exc_info.value)

def test_log_load_failure(calculator):
    # Patch load_history to simulate failure
    with patch("logging.basicConfig") as mock_basic:
        mock_basic.side_effect = Exception("Logging config failed")

        with pytest.raises(Exception):
            Calculator(config=calculator.config)

def test_validation_error_reraised(calculator):
    calc = Calculator(config=calculator.config)

    # Mock strategy that raises generic exception
    mock_strategy = MagicMock()
    mock_strategy.execute.side_effect = Exception("Boom")
    mock_strategy.__str__.return_value = "add"

    calc.operation_strategy = mock_strategy

    # Make validation pass
    with patch("app.calculator.InputValidator.validate_number") as mock_validate:
        mock_validate.side_effect = lambda x, config: Decimal(str(x))

        with pytest.raises(OperationError) as exc_info:
            calc.perform_operation(1, 2)

    assert "Operation failed: Boom" in str(exc_info.value)

def test_history_max_size_enforced(calculator):
    calculator.config.max_history_size = 2

    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)

    calculator.perform_operation(1, 1)
    calculator.perform_operation(2, 2)
    calculator.perform_operation(3, 3)

    assert len(calculator.history) == 2
    assert calculator.history[0].operand1 == Decimal("2")



@patch("app.calculator.logging.info")
@patch("app.calculator.pd.DataFrame.to_csv")
def test_save_empty_history(mock_to_csv, mock_log, calculator):

    calculator.clear_history()  # safest

    calculator.save_history()

    mock_log.assert_called_with("Empty history saved")



def test_history_file(calculator):

    with patch("app.calculator.pd.DataFrame.to_csv", side_effect=OperationError("Failed to load history")):
        with pytest.raises(OperationError) as exc_info:
            calculator.save_history()

@patch("app.calculator.logging.info")

def test_load_empty_history(mock_log, calculator):

    calculator.clear_history()  # safest
    calculator.save_history()

    calculator.load_history()

    mock_log.assert_called_with("Loaded empty history file")

def test_read_history_file_error(calculator):

    with patch("app.calculator.Path.exists", return_value=True), \
         patch("app.calculator.pd.read_csv", side_effect=Exception("Boom")):

        with pytest.raises(OperationError) as exc_info:
            calculator.load_history()

        assert "Failed to load history" in str(exc_info.value)

def test_get_history_dataframe(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)

    calculator.perform_operation(2, 3)

    df = calculator.get_history_dataframe()

    expected_df = pd.DataFrame([{
        'operation': str(operation),
        'operand1': '2',
        'operand2': '3',
        'result': '5',
        'timestamp': calculator.history[0].timestamp
    }])

    pd.testing.assert_frame_equal(df, expected_df)

def test_get_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    expected = ['Addition(2, 3) = 5']
    calculator.perform_operation(2, 3)
    result = calculator.show_history()

    assert expected == result

def test_undo_negative(calculator):
    calculator.undo_stack.clear()
    result =calculator.undo()
    assert False == result

def test_redo_negative(calculator):
    calculator.redo_stack.clear()
    result =calculator.redo()
    assert False == result


def test_memento_creation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)

    memento = CalculatorMemento(history=calculator.history.copy())

    assert memento.history == calculator.history
    assert isinstance(memento.timestamp, datetime.datetime)

def test_memento_to_dict(calculator):

    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)

    memento = CalculatorMemento(history=calculator.history.copy())
    data = memento.to_dict()

    assert "history" in data
    assert "timestamp" in data
    assert isinstance(data["history"], list)
    assert isinstance(data["timestamp"], str)

    # Verify serialized calculation structure
    assert data["history"][0]["operand1"] == "2"
    assert data["history"][0]["result"] == "5"

def test_memento_from_dict(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)

    original = CalculatorMemento(history=calculator.history.copy())
    data = original.to_dict()

    restored = CalculatorMemento.from_dict(data)

    assert isinstance(restored, CalculatorMemento)
    assert restored.timestamp == original.timestamp
    assert len(restored.history) == 1
    assert restored.history[0].operand1 == original.history[0].operand1


@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_undo_positive(mock_print, mock_input):
    with patch('app.calculator.Calculator.undo') as mock_undo:
        calculator_repl()
        mock_undo.assert_called_once()
        mock_print.assert_any_call("Operation undone")

@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_undo_negative(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Nothing to undo")


@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_redo_positive(mock_print, mock_input):
    with patch('app.calculator.Calculator.redo') as mock_redo:
        calculator_repl()
        mock_redo.assert_called_once()
        mock_print.assert_any_call("Operation redone")

@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_redo_negative(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Nothing to redo")

@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_calculator_repl_save_positive(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save:
        calculator_repl()
        assert mock_save.call_count == 2
        mock_print.assert_any_call("History saved successfully")

        
@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_calculator_repl_save_negative(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history', side_effect=Exception("Save failed")) as mock_save:
        calculator_repl()
        assert mock_save.call_count == 2
        mock_print.assert_any_call("Error saving history: Save failed")

@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_calculator_repl_load_positive(mock_print, mock_input):
    with patch('app.calculator.Calculator.load_history') as mock_load:
        calculator_repl()
        assert mock_load.call_count == 2
        mock_print.assert_any_call("History loaded successfully")

@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_calculator_repl_load_negative(mock_print, mock_input):
    with patch('app.calculator.Calculator.load_history', side_effect=Exception("Load failed")) as mock_load:
        calculator_repl()
        assert mock_load.call_count == 2
        mock_print.assert_any_call("Error loading history: Load failed")


@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel_a(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")


@patch('builtins.input', side_effect=['add', '2,','cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel_b(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")


@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_repl_perform_operation_error(mock_print, mock_input):
    # Patch the Calculator inside the REPL to raise OperationError
    with patch('app.calculator.Calculator.perform_operation', side_effect=OperationError("boom")):
        with patch('app.calculator.Calculator.set_operation'):
            calculator_repl()
    
    mock_print.assert_any_call("Error: boom")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_repl_unexpected_error(mock_print, mock_input):

    with patch('app.calculator.Calculator.perform_operation', side_effect=Exception("unexpected")):
        with patch('app.calculator.Calculator.set_operation'):
            calculator_repl()
    
    mock_print.assert_any_call("Unexpected error: unexpected")

@patch('builtins.input', side_effect=['foobar', 'exit'])
@patch('builtins.print')
def test_repl_unknown_command(mock_print, mock_input):

    calculator_repl()
    
    mock_print.assert_any_call("Unknown command: 'foobar'. Type 'help' for available commands.")



@patch('builtins.input', side_effect=EOFError)
@patch('builtins.print')
def test_repl_eof_error(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nInput terminated. Exiting...")


@patch('builtins.input', side_effect=[KeyboardInterrupt, 'exit'])
@patch('builtins.print')
def test_repl_keyboard_interrupt_error(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nOperation cancelled")

def test_inner_exception():
    """
    Simulate an unexpected exception during the REPL loop.
    It should print 'Error: ...' and continue running.
    """
    # Side effects:
    # - First input raises RuntimeError (to hit inner Exception)
    # - Second input returns 'exit' (to terminate loop)
    side_effects = [RuntimeError("oops"), 'exit']

    with patch("builtins.input", side_effect=side_effects):
        with patch("builtins.print") as mock_print:
            calculator_repl()

            # Check that the inner exception message was printed
            mock_print.assert_any_call("Error: oops")
            # Check that goodbye message was printed
            mock_print.assert_any_call("Goodbye!")

def test_outer_fatal_exception():
    """Test that a fatal error during REPL initialization is handled."""
    with patch("app.calculator_repl.Calculator", side_effect=Exception("init fail")):
        with patch("builtins.print") as mock_print, \
             patch("logging.error") as mock_log:
            try:
                calculator_repl()
            except Exception as e:
                assert str(e) == "init fail"
                printed = [args[0] for args, _ in mock_print.call_args_list]
                assert "Fatal error: init fail" in printed
                mock_log.assert_any_call("Fatal error in calculator REPL: init fail")