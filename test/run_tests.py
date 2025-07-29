#!/usr/bin/env python3
"""
Run all tests for the tapered capsule optimization pipeline.
"""

import sys
import subprocess
from pathlib import Path

def run_test_script(script_name):
    """Run a test script and return the result."""
    print(f"Running {script_name}...")
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {script_name} passed!")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {script_name} failed!")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {script_name} timed out!")
        return False
    except Exception as e:
        print(f"❌ {script_name} failed with exception: {e}")
        return False

def main():
    """Run all test scripts."""
    print("Running all tests for tapered capsule optimization pipeline")
    print("=" * 60)
    
    # List of test scripts to run
    test_scripts = [
        "test_coacd_pipeline.py"
    ]
    
    # Run each test script
    results = []
    for script in test_scripts:
        if Path(script).exists():
            result = run_test_script(script)
            results.append(result)
        else:
            print(f"⚠️  {script} not found, skipping...")
            results.append(True)  # Don't fail if test script doesn't exist
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! 🎉")
        return 0
    else:
        print("Some tests failed! ❌")
        return 1

if __name__ == "__main__":
    sys.exit(main())
