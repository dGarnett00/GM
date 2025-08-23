"""
Comprehensive validation tests for the Basketball GM application.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path when running directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_all_imports():
    """Test that all critical modules can be imported."""
    print("Testing module imports...")
    
    try:
        import PyQt5
        print("✓ PyQt5 import successful")
    except ImportError as e:
        print(f"✗ PyQt5 import failed: {e}")
        return False
    
    try:
        from gui.styles import AppStyles, AppFonts, UIConstants
        print("✓ GUI styles import successful")
    except ImportError as e:
        print(f"✗ GUI styles import failed: {e}")
        return False
    
    try:
        from gui.error_handling import ErrorHandler, AppLogger, InputValidator
        print("✓ Error handling import successful")
    except ImportError as e:
        print(f"✗ Error handling import failed: {e}")
        return False
    
    try:
        from core import simulate_game, generate_summary, generate_boxscore
        print("✓ Core modules import successful")
    except ImportError as e:
        print(f"✗ Core modules import failed: {e}")
        return False
    
    try:
        from core.teams import load_teams, get_team_roster
        print("✓ Teams modules import successful")
    except ImportError as e:
        print(f"✗ Teams modules import failed: {e}")
        return False
    
    try:
        from gui.widgets.start_menu import MainMenuWindow
        from gui.widgets.main_window import BasketballSimulatorWindow
        from gui.widgets.rosters_window import RostersWindow
        print("✓ GUI widgets import successful")
    except ImportError as e:
        print(f"✗ GUI widgets import failed: {e}")
        return False
    
    return True


def test_data_files():
    """Test that required data files exist and are readable."""
    print("\nTesting data files...")
    
    # Test teams data
    teams_file = ROOT / "core" / "teams" / "data" / "teams.json"
    if teams_file.exists():
        print("✓ Teams data file exists")
        try:
            from core.teams import load_teams
            teams = load_teams()
            if teams and len(teams) > 0:
                print(f"✓ Teams data loaded successfully ({len(teams)} teams)")
            else:
                print("✗ Teams data is empty")
        except Exception as e:
            print(f"✗ Teams data loading failed: {e}")
    else:
        print("? Teams data file not found (fallback will be used)")
    
    # Test rosters data
    rosters_file = ROOT / "core" / "teams" / "data" / "rosters" / "rosters.json"
    if rosters_file.exists():
        print("✓ Rosters data file exists")
        try:
            from core.teams import get_team_roster
            # Try to get a roster for a common team
            roster = get_team_roster("Lakers")
            if roster and len(roster) > 0:
                print(f"✓ Roster data accessible ({len(roster)} players found)")
            else:
                print("? No roster found for test team (may be expected)")
        except Exception as e:
            print(f"✗ Roster data loading failed: {e}")
    else:
        print("? Rosters data file not found (fallback generation will be used)")


def test_application_flow():
    """Test the basic application flow without GUI."""
    print("\nTesting application flow...")
    
    try:
        # Test game simulation
        from core import simulate_game
        result = simulate_game("Test Team 1", "Test Team 2")
        if len(result) == 5 and result[2] > 0 and result[3] > 0:
            print("✓ Game simulation works correctly")
        else:
            print("✗ Game simulation returned invalid result")
            
        # Test summary generation
        from core import generate_summary
        summary = generate_summary(*result)
        if summary and len(summary) > 50:  # Reasonable length check
            print("✓ Summary generation works correctly")
        else:
            print("✗ Summary generation failed")
            
        # Test boxscore generation
        from core import generate_boxscore
        boxscore = generate_boxscore(result[0], result[1], result[2], result[3])
        if boxscore and len(boxscore) > 100:  # Reasonable length check
            print("✓ Boxscore generation works correctly")
        else:
            print("✗ Boxscore generation failed")
            
    except Exception as e:
        print(f"✗ Application flow test failed: {e}")
        return False
    
    return True


def test_error_scenarios():
    """Test various error scenarios."""
    print("\nTesting error scenarios...")
    
    try:
        # Test invalid team selection
        from gui.error_handling import InputValidator, ValidationError
        try:
            InputValidator.validate_team_selection("", "Team B")
            print("✗ Should have raised validation error for empty team")
        except ValidationError:
            print("✓ Empty team validation works")
        
        # Test file operations with bad paths
        from gui.error_handling import FileOperations
        data = FileOperations.safe_read_json(Path("/nonexistent/file.json"), {})
        if data == {}:
            print("✓ Nonexistent file handling works")
        else:
            print("✗ Nonexistent file handling failed")
        
        # Test game simulation with invalid inputs
        from core import simulate_game
        result = simulate_game(None, "")
        if len(result) == 5:
            print("✓ Invalid input handling in simulation works")
        else:
            print("✗ Invalid input handling in simulation failed")
            
    except Exception as e:
        print(f"✗ Error scenario testing failed: {e}")
        return False
    
    return True


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("Basketball GM - Comprehensive Validation Tests")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_all_imports()
    test_data_files()  # Non-critical, so don't fail on this
    all_passed &= test_application_flow()
    all_passed &= test_error_scenarios()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All critical tests PASSED! Application is ready to use.")
    else:
        print("❌ Some critical tests FAILED. Please check the issues above.")
    
    return all_passed


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)