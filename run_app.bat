@echo off
REM This batch file runs the basketball simulator app without leaving a terminal window open
REM It will install PyQt5 if it is not already installed

pythonw -c "import PyQt5" 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    pythonw -m pip install pyqt5
)

start "" pythonw basketball_simulator.py
exit
