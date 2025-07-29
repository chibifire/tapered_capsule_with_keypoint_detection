#!/usr/bin/env python3
"""
Test script for the CoACD-based Tapered Capsule Optimization Pipeline.
"""

import sys
from pathlib import Path
from coacd_capsule_pipeline import CoACDCapsulePipeline

def test_pipeline():
    """Test the CoACD capsule pipeline with a sample VRM file."""
    
    # Look for sample VRM files
    sample_files = list(Path(".").glob("*.vrm"))
    if not sample_files:
        print("No VRM files found in current directory")
        return False
    
    # Use the first VRM file found
    vrm_file = sample_files[0]
    print(f"Testing pipeline with VRM file: {vrm_file}")
    
    try:
        # Create pipeline instance
        pipeline = CoACDCapsulePipeline(str(vrm_file))
        
        # Run complete pipeline with reduced parameters for testing
        success = pipeline.run_complete_pipeline(
            coacd_threshold=0.1,  # Higher threshold for faster processing
            witness_points=1000,  # Fewer points for faster processing
            max_capsules=20       # Limit capsules for testing
        )
        
        if success:
            print("✅ Pipeline test completed successfully!")
            return True
        else:
            print("❌ Pipeline test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during pipeline test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
