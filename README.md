# Basketball Game Simulator

A modern, modular desktop app (PyQt5) for simulating exhibition basketball games.

## Structure

- main.py — App entry point
- gui/ — UI package
	- widgets/main_window.py — Main window (menu + simulator)
	- dialogs/ — Placeholders for future dialogs
- core/ — Domain logic
	- game/ — Simulation + summary generation
		- sim.py — simulate_game, generate_summary
	- boxscore/ — Box score generation
		- generate.py — generate_boxscore
- simulation/ — Legacy shim forwarding to core/ (safe to remove later)
- ui/ — Legacy stub pointing to new GUI (safe to remove later)
- config/, resources/ — Reserved for settings/assets

## Run

1. Install requirements: `pip install -r requirements.txt`
2. Start the app: `python main.py`

Windows: double-click `run_app.bat` to auto-install PyQt5 (if needed) and launch.
