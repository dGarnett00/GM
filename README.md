# Basketball GM (Simulation Removed)

A modern, modular desktop app (PyQt5). Game simulation features have been removed in this build; box score utilities and team browsing remain.

## Structure

- main.py — App entry point
- gui/ — UI package
	- widgets/main_window.py — Main window (menu + simulator)
	- dialogs/ — Placeholders for future dialogs
- core/ — Domain logic
	- boxscore/ — Box score generation
		- generate.py — generate_boxscore
- simulation/ — Removed
- ui/ — Legacy stub pointing to new GUI (safe to remove later)
- config/, resources/ — Reserved for settings/assets

## Run

1. Install requirements: `pip install -r requirements.txt`
2. Start the app: `python main.py`

Windows: double-click `run_app.bat` to auto-install PyQt5 (if needed) and launch.

## Notes

- Game simulation, summaries, and live event feeds have been removed.
- The main window retains team selection and result pane; simulate actions are disabled.
