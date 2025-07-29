#!/usr/bin/env python3
"""
Test script to visualize a tapered capsule to verify the fix for top hemisphere winding order.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from minizinc_to_gltf import GLTFCapsuleGenerator
import json

def test_capsule_visualization():
    """Generate a simple tapered capsule and save it as GLTF for visualization."""
    print("Testing capsule visualization...")
    
    # Create generator
    generator = GLTFCapsuleGenerator()
    
    # Create a simple tapered capsule (wider at bottom, narrower at top)
    capsules = [
        {
            'position': (0, 0, 0),
            'length': 2.0,
            'radius1': 0.5,  # Bottom radius
            'radius2': 0.3,  # Top radius
            'bone_name': 'TestCapsule'
        }
    ]
    
    # Generate GLTF
    gltf_data = generator.generate_gltf(capsules)
    
    # Save to file
    output_file = "test_capsule.gltf"
    generator.save_gltf(output_file)
    print(f"Generated test capsule: {output_file}")
    
    # Print some stats
    total_vertices = sum(gltf_data["accessors"][mesh["primitives"][0]["attributes"]["POSITION"]]["count"] 
                        for mesh in gltf_data["meshes"] if "primitives" in mesh)
    print(f"Total vertices: {total_vertices}")
    print(f"Total meshes: {len(gltf_data['meshes'])}")
    
    print("You can now open the GLTF file in a viewer to verify the capsule geometry.")
    print("The capsule should be wider at the bottom (radius 0.5) and narrower at the top (radius 0.3).")
    print("Both hemispheres should be correctly oriented (not inside out).")

if __name__ == "__main__":
    test_capsule_visualization()
