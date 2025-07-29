#!/usr/bin/env python3
"""
Run all tests for the tapered capsule optimization project.
"""

import sys
import subprocess
from pathlib import Path

def run_test_script(script_name: str) -> bool:
    """Run a test script and return True if successful."""
    print(f"\n🧪 Running {script_name}...")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {script_name} passed")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {script_name} failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {script_name} timed out")
        return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Run all test scripts in the project."""
    print("🚀 Running all tests for tapered capsule optimization project")
    print("=" * 60)
    
    # List of test scripts to run
    test_scripts = [
        "test_coacd_pipeline.py"
    ]
    
    # Check if test scripts exist
    existing_scripts = []
    for script in test_scripts:
        if Path(script).exists():
            existing_scripts.append(script)
        else:
            print(f"⚠️  Test script not found: {script}")
    
    if not existing_scripts:
        print("❌ No test scripts found!")
        return False
    
    # Run each test script
    passed = 0
    failed = 0
    
    for script in existing_scripts:
        if run_test_script(script):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"💥 {failed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
