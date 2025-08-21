from PyQt5.QtWidgets import QApplication
import sys
from gui.widgets.main_window import BasketballSimulatorWindow

def main():
    app = QApplication(sys.argv)
    window = BasketballSimulatorWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
