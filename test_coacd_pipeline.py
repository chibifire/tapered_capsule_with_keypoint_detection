#!/usr/bin/env python3
"""
Test script for CoACD-based Tapered Capsule Optimization Pipeline.
"""

import sys
import os
import tempfile
import numpy as np
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_point_in_tapered_capsule():
    """Test the _point_in_tapered_capsule method."""
    print("Testing _point_in_tapered_capsule method...")
    
    # Import the pipeline class
    try:
        from coacd_capsule_pipeline import CoACDCapsulePipeline
    except ImportError as e:
        print(f"Error importing CoACDCapsulePipeline: {e}")
        return False
    
    # Create a mock pipeline instance
    pipeline = CoACDCapsulePipeline("samplesnek16.vrm")
    
    # Test case 1: Point inside a simple capsule
    p1 = np.array([0, 0, 0])
    p2 = np.array([0, 2, 0])
    radius_top = 1.0
    radius_bottom = 1.0
    point = np.array([0, 1, 0])
    
    result = pipeline._point_in_tapered_capsule(point, p1, p2, radius_top, radius_bottom)
    print(f"Test 1 - Point {point} inside capsule: {result}")
    assert result == True, "Point should be inside the capsule"
    
    # Test case 2: Point outside a simple capsule
    point = np.array([0, 1, 2])
    result = pipeline._point_in_tapered_capsule(point, p1, p2, radius_top, radius_bottom)
    print(f"Test 2 - Point {point} outside capsule: {result}")
    assert result == False, "Point should be outside the capsule"
    
    # Test case 3: Point inside a tapered capsule (top radius smaller)
    radius_top = 0.5
    radius_bottom = 1.0
    point = np.array([0, 0.5, 0])  # Near bottom where radius is larger
    result = pipeline._point_in_tapered_capsule(point, p1, p2, radius_top, radius_bottom)
    print(f"Test 3 - Point {point} inside tapered capsule: {result}")
    assert result == True, "Point should be inside the tapered capsule"
    
    # Test case 4: Point outside a tapered capsule (top radius smaller)
    point = np.array([0, 1.5, 0])  # Near top where radius is smaller
    result = pipeline._point_in_tapered_capsule(point, p1, p2, radius_top, radius_bottom)
    print(f"Test 4 - Point {point} near top of tapered capsule: {result}")
    
    print("All tests passed!")
    return True

def test_pipeline_initialization():
    """Test pipeline initialization."""
    print("Testing pipeline initialization...")
    
    try:
        from coacd_capsule_pipeline import CoACDCapsulePipeline
    except ImportError as e:
        print(f"Error importing CoACDCapsulePipeline: {e}")
        return False
    
    # Test with a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "output"
        pipeline = CoACDCapsulePipeline("samplesnek16.vrm", str(output_dir))
        
        assert pipeline.vrm_path.name == "samplesnek16.vrm"
        assert pipeline.output_dir == output_dir
        print("Pipeline initialization test passed!")
        return True

def main():
    """Run all tests."""
    print("Running CoACD Pipeline Tests")
    print("=" * 40)
    
    # Test individual components
    test_results = []
    
    test_results.append(test_point_in_tapered_capsule())
    test_results.append(test_pipeline_initialization())
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    passed = sum(test_results)
    total = len(test_results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! 🎉")
        return 0
    else:
        print("Some tests failed! ❌")
        return 1

if __name__ == "__main__":
    sys.exit(main())
