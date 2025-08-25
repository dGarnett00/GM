import sys
import os
import traceback
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt

def main():
    # Configure logging early
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(base_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        log_path = os.path.join(logs_dir, 'app.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[logging.FileHandler(log_path, encoding='utf-8'), logging.StreamHandler(sys.stdout)]
        )
        logging.info('Starting Basketball GM app')
    except Exception:
        # If logging setup fails, continue without it
        pass

    # Create Qt application
    try:
        app = QApplication(sys.argv)
        # Apply global QSS stylesheet
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            styles_dir = os.path.join(base_dir, 'gui', 'styles')
            buf = []
            # Load base.qss first if present
            base_qss = os.path.join(styles_dir, 'base.qss')
            if os.path.exists(base_qss):
                with open(base_qss, 'r', encoding='utf-8') as f:
                    buf.append(f.read())
            # Then load window- and component-level QSS in a deterministic order
            ordered_dirs = [os.path.join(styles_dir, 'windows'), os.path.join(styles_dir, 'components')]
            for d in ordered_dirs:
                if not os.path.isdir(d):
                    continue
                for fname in sorted(os.listdir(d)):
                    if not fname.lower().endswith('.qss'):
                        continue
                    path = os.path.join(d, fname)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            buf.append(f.read())
                    except Exception:
                        continue
            qss_text = '\n\n'.join(buf) if buf else ''
            # Load theme variables and substitute $KEY occurrences
            vars_path = os.path.join(styles_dir, 'theme_vars.qss')
            vars_map = {}
            if os.path.exists(vars_path):
                try:
                    with open(vars_path, 'r', encoding='utf-8') as vf:
                        for line in vf:
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue
                            if '=' in line:
                                k, v = line.split('=', 1)
                                vars_map[k.strip()] = v.strip()
                except Exception:
                    vars_map = {}
            # simple substitution: replace $KEY with value
            if vars_map and qss_text:
                for k, v in vars_map.items():
                    qss_text = qss_text.replace(f"${k}", v)
            if qss_text:
                app.setStyleSheet(qss_text)
        except Exception:
            # Don't block startup if styling fails
            pass
    except Exception:
        # If even QApplication fails, we cannot continue with a GUI
        traceback.print_exc()
        print('FATAL: Unable to start Qt application. See traceback above.')
        sys.exit(1)

    # Global exception handler to prevent hard crash dialogs
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        try:
            logging.error('Uncaught exception:\n%s', tb)
        except Exception:
            pass
        # Show a simple error window but keep app running
        show_fallback_window(f"Uncaught exception: {exc_type.__name__}", tb)

    sys.excepthook = handle_exception

    # Fallback window definition kept inside main to avoid extra imports
    def show_fallback_window(title: str, details: str):
        w = QWidget()
        w.setWindowTitle('Basketball GM — Startup Issue')
        layout = QVBoxLayout()
        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignLeft)
        lbl.setStyleSheet('color:#eebbc3')
        details_box = QTextEdit()
        details_box.setReadOnly(True)
        details_box.setPlainText(details)
        btn = QPushButton('Exit')
        btn.clicked.connect(w.close)
        layout.addWidget(lbl)
        layout.addWidget(details_box)
        layout.addWidget(btn)
        w.setLayout(layout)
        w.resize(640, 360)
        w.show()
        return w

    # Try to import and show the main menu lazily, so a bad import won't kill the app
    try:
        from gui.widgets.start_menu import MainMenuWindow  # Local import for robustness
        window = MainMenuWindow()
        window.show()
    except Exception:
        tb = traceback.format_exc()
        try:
            logging.exception('Failed to initialize MainMenuWindow')
        except Exception:
            pass
        # Show fallback error window but keep the event loop alive
        _fallback = show_fallback_window('Failed to initialize the main menu.', tb)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
