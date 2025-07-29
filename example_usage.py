#!/usr/bin/env python3
"""
Example usage of the CoACD-based Tapered Capsule Optimization Pipeline.
"""

import sys
import os
from pathlib import Path

def main():
    # Check if we have a sample VRM file to work with
    sample_vrm = Path("samplesnek16.vrm")
    
    if not sample_vrm.exists():
        print("Sample VRM file not found. Please provide a VRM file to process.")
        print("Usage: python3 example_usage.py <input.vrm>")
        return
    
    # Import our pipeline
    try:
        from coacd_capsule_pipeline import CoACDCapsulePipeline
    except ImportError as e:
        print(f"Error importing pipeline: {e}")
        print("Make sure all dependencies are installed.")
        return
    
    print("CoACD-based Tapered Capsule Optimization Pipeline Example")
    print("=" * 60)
    
    # Create pipeline instance
    pipeline = CoACDCapsulePipeline(str(sample_vrm))
    
    # Run with default parameters
    print(f"Processing: {sample_vrm}")
    print("Using default parameters:")
    print("  CoACD threshold: 0.05")
    print("  Witness points: 5000")
    print("  Max capsules: 50")
    print("-" * 60)
    
    success = pipeline.run_complete_pipeline(
        coacd_threshold=0.05,
        witness_points=5000,
        max_capsules=50
    )
    
    if success:
        print("-" * 60)
        print("Pipeline completed successfully!")
        print(f"Output files are in: {pipeline.output_dir}")
    else:
        print("-" * 60)
        print("Pipeline failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
