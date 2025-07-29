#!/usr/bin/env python3
"""
Example usage of the tapered capsule public API.
"""

import sys
import os

# Add the current directory to the path so we can import the tapered_capsule module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import tapered_capsule


def main():
    """Demonstrate the public API usage."""
    print("Tapered Capsule Public API Example")
    print("=" * 40)
    
    # Show version information
    print(f"Version: {tapered_capsule.__version__}")
    print(f"Author: {tapered_capsule.__author__}")
    print()
    
    # Show available classes and functions
    print("Available classes:")
    for item in tapered_capsule.__all__:
        print(f"  - {item}")
    print()
    
    print("Available functions:")
    functions = [attr for attr in dir(tapered_capsule) if callable(getattr(tapered_capsule, attr)) and not attr.startswith('_')]
    for func in functions:
        if func not in tapered_capsule.__all__:
            print(f"  - {func}")
    print()
    
    print("Example usage:")
    print("  # Analyze a VRM file")
    print("  analyzer = tapered_capsule.VRMMeshAnalyzer()")
    print("  # analyzer.load_vrm_file('model.vrm')")
    print()
    print("  # Run complete pipeline")
    print("  # tapered_capsule.generate_capsules_from_vrm('model.vrm', max_capsules=8)")
    print()
    print("  # Generate skinned capsules from results")
    print("  # tapered_capsule.generate_skinned_capsules_from_vrm(")
    print("  #     'model.vrm', 'results.txt', 'output.gltf')")
    print()


if __name__ == "__main__":
    main()
