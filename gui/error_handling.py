"""Error handling utilities and logging for the Basketball GM application."""

import logging
import traceback
import sys
from pathlib import Path
from typing import Optional, Callable, Any
from functools import wraps

from PyQt5.QtWidgets import QMessageBox, QWidget


class AppLogger:
    """Centralized logging for the application."""
    
    _logger: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get or create the application logger."""
        if cls._logger is None:
            cls._logger = logging.getLogger('basketball_gm')
            cls._logger.setLevel(logging.INFO)
            
            # Create logs directory if it doesn't exist
            log_dir = Path(__file__).parent.parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            # File handler
            file_handler = logging.FileHandler(log_dir / 'basketball_gm.log')
            file_handler.setLevel(logging.INFO)
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            cls._logger.addHandler(file_handler)
            cls._logger.addHandler(console_handler)
        
        return cls._logger


class ErrorHandler:
    """Centralized error handling with user-friendly messages."""
    
    @staticmethod
    def show_error(parent: Optional[QWidget], title: str, message: str, 
                   details: Optional[str] = None) -> None:
        """Show an error dialog to the user."""
        logger = AppLogger.get_logger()
        logger.error(f"{title}: {message}")
        if details:
            logger.error(f"Details: {details}")
        
        if parent is not None:
            msg = QMessageBox(parent)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle(title)
            msg.setText(message)
            if details:
                msg.setDetailedText(details)
            msg.exec_()
        else:
            print(f"ERROR: {title}: {message}")
            if details:
                print(f"Details: {details}")
    
    @staticmethod
    def show_warning(parent: Optional[QWidget], title: str, message: str) -> None:
        """Show a warning dialog to the user."""
        logger = AppLogger.get_logger()
        logger.warning(f"{title}: {message}")
        
        if parent is not None:
            QMessageBox.warning(parent, title, message)
        else:
            print(f"WARNING: {title}: {message}")
    
    @staticmethod
    def show_info(parent: Optional[QWidget], title: str, message: str) -> None:
        """Show an info dialog to the user."""
        logger = AppLogger.get_logger()
        logger.info(f"{title}: {message}")
        
        if parent is not None:
            QMessageBox.information(parent, title, message)
        else:
            print(f"INFO: {title}: {message}")
    
    @staticmethod
    def handle_exception(parent: Optional[QWidget], operation: str, 
                        exception: Exception) -> None:
        """Handle an exception with proper logging and user notification."""
        logger = AppLogger.get_logger()
        error_msg = f"Error during {operation}: {str(exception)}"
        logger.error(error_msg, exc_info=True)
        
        user_msg = f"An error occurred while {operation}."
        details = f"{type(exception).__name__}: {str(exception)}\n\n{traceback.format_exc()}"
        
        ErrorHandler.show_error(parent, "Operation Failed", user_msg, details)


def safe_execute(operation_name: str, parent: Optional[QWidget] = None):
    """Decorator to safely execute functions with error handling."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_exception(parent, operation_name, e)
                return None
        return wrapper
    return decorator


def safe_execute_method(operation_name: str):
    """Decorator for class methods that need error handling (parent is self)."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                parent = self if isinstance(self, QWidget) else None
                ErrorHandler.handle_exception(parent, operation_name, e)
                return None
        return wrapper
    return decorator


class FileOperations:
    """Safe file operations with proper error handling."""
    
    @staticmethod
    def safe_read_json(file_path: Path, default_value: Any = None, 
                      parent: Optional[QWidget] = None) -> Any:
        """Safely read a JSON file with error handling."""
        try:
            if not file_path.exists():
                AppLogger.get_logger().info(f"File not found: {file_path}, using default")
                return default_value
            
            with file_path.open('r', encoding='utf-8') as f:
                import json
                data = json.load(f)
                AppLogger.get_logger().info(f"Successfully loaded {file_path}")
                return data
                
        except json.JSONDecodeError as e:
            ErrorHandler.handle_exception(
                parent, f"parsing JSON file {file_path.name}", e
            )
            return default_value
        except Exception as e:
            ErrorHandler.handle_exception(
                parent, f"reading file {file_path.name}", e
            )
            return default_value
    
    @staticmethod
    def safe_write_file(file_path: Path, content: str, 
                       parent: Optional[QWidget] = None) -> bool:
        """Safely write content to a file with error handling."""
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with file_path.open('w', encoding='utf-8') as f:
                f.write(content)
            
            AppLogger.get_logger().info(f"Successfully wrote to {file_path}")
            return True
            
        except Exception as e:
            ErrorHandler.handle_exception(
                parent, f"writing to file {file_path.name}", e
            )
            return False


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_team_selection(team1: str, team2: str) -> None:
        """Validate team selections for game simulation."""
        if not team1 or not team1.strip():
            raise ValidationError("First team selection is empty")
        
        if not team2 or not team2.strip():
            raise ValidationError("Second team selection is empty")
        
        if team1.strip() == team2.strip():
            raise ValidationError("Cannot select the same team twice")
    
    @staticmethod
    def validate_file_path(file_path: Path, must_exist: bool = True) -> None:
        """Validate a file path."""
        if must_exist and not file_path.exists():
            raise ValidationError(f"File does not exist: {file_path}")
        
        if must_exist and not file_path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")
        
        # Check if parent directory exists for writing
        if not must_exist and not file_path.parent.exists():
            raise ValidationError(f"Parent directory does not exist: {file_path.parent}")