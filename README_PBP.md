Play-by-Play high-fidelity rendering

This project supports a lightweight play-by-play viewer by default (QTextBrowser).

For full HTML/CSS/JS fidelity (the widget will render complex HTML exactly as a browser), install PyQtWebEngine in the same environment as PyQt5:

Windows (cmd.exe):

```
python -m pip install PyQtWebEngine
```

After installing, restart the app. The Exhibition window will use QWebEngineView automatically.

If PyQtWebEngine is not installed, the app falls back to QTextBrowser and will still support stepwise playback from simple HTML fragments.
