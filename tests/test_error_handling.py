"""
Tests for error handling and validation functionality.
"""
import sys
import tempfile
import json
from pathlib import Path

# Ensure project root is in sys.path when running directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gui.error_handling import InputValidator, ValidationError, FileOperations
from core.teams.loader import load_teams
from core.teams.rosters import get_team_roster


def test_input_validation():
    """Test input validation functionality."""
    # Test valid team selections
    try:
        InputValidator.validate_team_selection("Team A", "Team B")
        print("✓ Valid team selection passes")
    except ValidationError:
        print("✗ Valid team selection should not raise error")
        
    # Test empty team selections
    try:
        InputValidator.validate_team_selection("", "Team B")
        print("✗ Empty team selection should raise error")
    except ValidationError:
        print("✓ Empty team selection properly rejected")
        
    # Test same team selections
    try:
        InputValidator.validate_team_selection("Team A", "Team A")
        print("✗ Same team selection should raise error")
    except ValidationError:
        print("✓ Same team selection properly rejected")


def test_file_operations():
    """Test safe file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test.json"
        
        # Test writing file
        success = FileOperations.safe_write_file(temp_path, '{"test": "data"}')
        if success:
            print("✓ File writing successful")
        else:
            print("✗ File writing failed")
            
        # Test reading valid JSON
        data = FileOperations.safe_read_json(temp_path, default_value={})
        if data == {"test": "data"}:
            print("✓ JSON reading successful")
        else:
            print("✗ JSON reading failed")
            
        # Test reading non-existent file
        non_existent = Path(temp_dir) / "missing.json"
        data = FileOperations.safe_read_json(non_existent, default_value={"default": True})
        if data == {"default": True}:
            print("✓ Missing file returns default")
        else:
            print("✗ Missing file handling failed")
            
        # Test reading invalid JSON
        invalid_path = Path(temp_dir) / "invalid.json"
        FileOperations.safe_write_file(invalid_path, "invalid json content")
        data = FileOperations.safe_read_json(invalid_path, default_value={"fallback": True})
        if data == {"fallback": True}:
            print("✓ Invalid JSON returns default")
        else:
            print("✗ Invalid JSON handling failed")


def test_teams_loading_error_handling():
    """Test teams loading with various error conditions."""
    # Test normal loading
    teams = load_teams()
    if teams and len(teams) > 0:
        print(f"✓ Teams loaded successfully ({len(teams)} teams)")
    else:
        print("✗ Teams loading failed")
        
    # Test loading from non-existent path
    teams = load_teams(Path("/nonexistent/path/teams.json"))
    if teams and len(teams) > 0:
        print(f"✓ Fallback teams loaded from non-existent path ({len(teams)} teams)")
    else:
        print("✗ Fallback teams loading failed")


def test_roster_loading_error_handling():
    """Test roster loading with various error conditions."""
    # Test normal roster loading
    roster = get_team_roster("Los Angeles Lakers")  # Should exist in real data
    if roster and len(roster) > 0:
        print(f"✓ Roster loaded successfully ({len(roster)} players)")
    else:
        print("? No roster found for Lakers (may be expected if no data file)")
        
    # Test non-existent team
    roster = get_team_roster("Nonexistent Team")
    if roster and len(roster) > 0:
        print(f"✓ Fallback roster generated for non-existent team ({len(roster)} players)")
    else:
        print("✗ Fallback roster generation failed")
        
    # Test empty team name
    roster = get_team_roster("")
    if not roster or len(roster) == 0:
        print("✓ Empty team name returns empty roster")
    else:
        print("✗ Empty team name should return empty roster")


def test_game_simulation_edge_cases():
    """Test game simulation with edge cases."""
    from core import simulate_game, generate_summary, generate_boxscore
    
    # Test normal simulation
    try:
        result = simulate_game("Team A", "Team B")
        if len(result) == 5 and all(result[:4]):
            print("✓ Normal game simulation successful")
        else:
            print("✗ Normal game simulation failed")
    except Exception as e:
        print(f"✗ Normal game simulation threw exception: {e}")
        
    # Test empty team names
    try:
        result = simulate_game("", "")
        if len(result) == 5:
            print("✓ Empty team names handled gracefully")
        else:
            print("✗ Empty team names not handled properly")
    except Exception as e:
        print(f"✗ Empty team names threw exception: {e}")
        
    # Test None inputs
    try:
        result = simulate_game(None, None)
        if len(result) == 5:
            print("✓ None inputs handled gracefully")
        else:
            print("✗ None inputs not handled properly")
    except Exception as e:
        print(f"✗ None inputs threw exception: {e}")
        
    # Test summary generation with invalid scores
    try:
        summary = generate_summary("Team A", "Team B", "invalid", None, "Team A")
        if summary and len(summary) > 0:
            print("✓ Invalid scores handled gracefully in summary")
        else:
            print("✗ Invalid scores not handled in summary")
    except Exception as e:
        print(f"✗ Summary with invalid scores threw exception: {e}")
        
    # Test boxscore generation with invalid inputs
    try:
        boxscore = generate_boxscore(None, "", -5, "invalid")
        if boxscore and len(boxscore) > 0:
            print("✓ Invalid inputs handled gracefully in boxscore")
        else:
            print("✗ Invalid inputs not handled in boxscore")
    except Exception as e:
        print(f"✗ Boxscore with invalid inputs threw exception: {e}")


def run_all_tests():
    """Run all error handling tests."""
    print("Running Error Handling Tests")
    print("=" * 40)
    
    print("\n1. Testing Input Validation:")
    test_input_validation()
    
    print("\n2. Testing File Operations:")
    test_file_operations()
    
    print("\n3. Testing Teams Loading:")
    test_teams_loading_error_handling()
    
    print("\n4. Testing Roster Loading:")
    test_roster_loading_error_handling()
    
    print("\n5. Testing Game Simulation Edge Cases:")
    test_game_simulation_edge_cases()
    
    print("\n" + "=" * 40)
    print("Error handling tests completed!")


if __name__ == "__main__":
    run_all_tests()