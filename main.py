from PyQt5.QtWidgets import QApplication
import sys
from gui.widgets.start_menu import MainMenuWindow

def main():
    app = QApplication(sys.argv)
    window = MainMenuWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
