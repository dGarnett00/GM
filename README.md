# Basketball GM - Exhibition Game Simulator

A PyQt5-based basketball game simulator featuring team management, game simulation, and detailed statistics.

## Features

- **Exhibition Games**: Simulate games between any two teams
- **Team Management**: Browse team rosters and information
- **Detailed Statistics**: Comprehensive box scores with player stats, team comparisons, and game highlights
- **Export Options**: Save results as HTML, copy to clipboard, or print
- **Robust Error Handling**: Graceful handling of missing data and user errors
- **Professional UI**: Clean, modern interface with consistent styling

## Installation

1. Ensure Python 3.8+ is installed
2. Install PyQt5:
   ```bash
   pip install PyQt5
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Main Menu
- **Exhibition**: Start a new game simulation
- **Rosters**: View team rosters and player information
- **Reload**: Restart the application to refresh data
- **Exit**: Close the application

### Game Simulation
- Select two teams from the dropdown menus
- Click "Simulate Game" to run the simulation
- View detailed results including:
  - Final score and game summary
  - Quarter-by-quarter breakdown
  - Complete player statistics
  - Team comparison metrics
  - Game MVP selection

### Menu Options
- **File Menu**: New games, team management, save/export options
- **View Menu**: Toggle fullscreen mode
- **Help Menu**: About information

## Technical Features

### Error Handling
- Comprehensive error handling throughout the application
- Graceful degradation when data files are missing
- Input validation for all user interactions
- Detailed logging for debugging

### Data Management
- JSON-based team and roster data
- Fallback data generation when files are unavailable
- Robust file I/O with proper error recovery

### Code Quality
- Centralized styling system for consistent UI
- Modular architecture with clear separation of concerns
- Comprehensive test suite
- Type hints and documentation

## Testing

Run the test suite to verify functionality:

```bash
# Run basic functionality tests
python tests/test_core_game.py

# Run error handling tests
python tests/test_error_handling.py

# Run comprehensive validation
python tests/test_comprehensive.py
```

## File Structure

```
├── main.py                 # Application entry point
├── gui/
│   ├── styles.py          # Centralized styling
│   ├── error_handling.py  # Error handling utilities
│   └── widgets/           # GUI components
├── core/
│   ├── game/              # Game simulation
│   ├── boxscore/          # Statistics generation
│   └── teams/             # Team and roster management
├── tests/                 # Test suite
└── logs/                  # Application logs
```

## Keyboard Shortcuts

- **Ctrl+N**: New Exhibition
- **Ctrl+R**: Randomize Teams
- **Ctrl+S**: Swap Teams
- **Ctrl+L**: Clear Results
- **Ctrl+Shift+S**: Save Results as HTML
- **Ctrl+Alt+C**: Copy Results to Clipboard
- **Ctrl+P**: Print Results
- **Ctrl+M**: Back to Main Menu
- **F11**: Toggle Fullscreen
- **ESC**: Exit fullscreen (when in fullscreen mode)

## Recent Improvements

### Version 1.0 (Latest)
- **Complete Error Handling**: Comprehensive error handling throughout the application
- **Centralized Styling**: Consistent UI design with centralized style management
- **Enhanced Data Loading**: Robust team and roster loading with fallback generation
- **Improved Simulation**: Better game simulation with enhanced statistics
- **Professional UI**: Cleaner interface with better user feedback
- **Comprehensive Testing**: Full test suite covering all functionality
- **Better Logging**: Application-wide logging for debugging and monitoring

## Contributing

The codebase follows these principles:
- Comprehensive error handling for all operations
- Centralized styling and configuration
- Clear separation of concerns
- Extensive testing and validation
- Professional code documentation

## License

This project is released under the MIT License.
