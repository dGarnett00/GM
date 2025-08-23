from PyQt5.QtWidgets import QApplication
import sys
import logging
from pathlib import Path

from gui.widgets.start_menu import MainMenuWindow
from gui.error_handling import AppLogger, ErrorHandler


def setup_logging():
    """Initialize application logging."""
    try:
        logger = AppLogger.get_logger()
        logger.info("Basketball GM application starting")
        return True
    except Exception as e:
        print(f"Failed to initialize logging: {e}")
        return False


def main():
    """Main application entry point with error handling."""
    # Setup logging first
    logging_ok = setup_logging()
    logger = logging.getLogger('basketball_gm') if logging_ok else None
    
    try:
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Basketball GM")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("Basketball GM")
        
        if logger:
            logger.info("Creating main window")
        
        window = MainMenuWindow()
        window.show()
        
        if logger:
            logger.info("Application started successfully")
        
        exit_code = app.exec_()
        
        if logger:
            logger.info(f"Application exiting with code {exit_code}")
        
        sys.exit(exit_code)
        
    except ImportError as e:
        error_msg = f"Missing required dependency: {e}"
        if "PyQt5" in str(e):
            error_msg += "\n\nPlease install PyQt5: pip install PyQt5"
        print(f"ERROR: {error_msg}")
        if logger:
            logger.error(error_msg)
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Failed to start application: {e}"
        print(f"ERROR: {error_msg}")
        if logger:
            logger.error(error_msg, exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
