#!/usr/bin/env python3
"""
Test the tapered capsule pipeline with a representative feminine avatar.
"""

import sys
import os

# Add the current directory to the path so we can import the tapered_capsule module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tapered_capsule


def main():
    """Test the pipeline with a feminine VRM avatar."""
    print("Testing Tapered Capsule Pipeline with Feminine Avatar")
    print("=" * 50)
    
    # Path to the feminine VRM avatar
    vrm_path = "thirdparty/vrm_samples/vroid/fem_vroid.vrm"
    
    # Check if the file exists
    if not os.path.exists(vrm_path):
        print(f"❌ VRM file not found: {vrm_path}")
        print("Please ensure the VRM samples are available in the thirdparty directory.")
        return False
    
    print(f"Using VRM file: {vrm_path}")
    
    # Suggested reasonable amount of capsules for a humanoid avatar
    # 8-12 capsules is typically sufficient for a good balance between accuracy and performance
    max_capsules = 10
    print(f"Using {max_capsules} capsules for optimization")
    
    try:
        print("\nStep 1: Analyzing VRM mesh...")
        analyzer = tapered_capsule.analyze_vrm_mesh(vrm_path, max_capsules)
        print("✅ VRM analysis completed successfully")
        
        print("\nStep 2: Running capsule generation pipeline...")
        success = tapered_capsule.generate_capsules_from_vrm(vrm_path, max_capsules, timeout=60)
        
        if success:
            print("✅ Capsule generation pipeline completed successfully")
            print(f"Output files have been generated in the output directory.")
        else:
            print("❌ Capsule generation pipeline failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("Test completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
