#!/usr/bin/env python3
"""
MiniZinc Data Generator - Single responsibility: Generate .dzn files from mesh analysis.
"""

from typing import Dict, Any, List
from pathlib import Path
import numpy as np
import json

class MiniZincDataGenerator:
    """Generates MiniZinc .dzn data files from mesh analysis results."""
    
    def __init__(self):
        pass
        
    def generate_cpsat_data(self, 
                            output_path: str, 
                            bone_analysis: Dict[str, Any], 
                            max_capsules: int, 
                            scale: int = 1000) -> bool:
        """
        Generates a MiniZinc .dzn file for CP-SAT solver.
        
        Args:
            output_path (str): Path to save the .dzn file.
            bone_analysis (Dict[str, Any]): Dictionary of bone analysis data.
            max_capsules (int): Maximum number of capsules to generate.
            scale (int): Scaling factor for integer precision.
        """
        
        output_path = Path(output_path)
        
        # Filter bones that have geometry data
        filtered_bones = [
            (name, data) for name, data in bone_analysis.items() 
            if 'vertex_count' in data and data['vertex_count'] > 0
        ]
        
        # Sort by vertex count to prioritize larger bones
        filtered_bones.sort(key=lambda x: x[1]['vertex_count'], reverse=True)
        
        # Limit to max_capsules
        selected_bones = filtered_bones[:max_capsules]
        
        n_capsules = len(selected_bones)
        
        bone_centers = []
        bone_sizes = []
        bone_rotations = []
        bone_directions = []
        bone_names = []
        
        # Calculate global min/max positions for all bones
        all_min_pos = np.array([float('inf')] * 3)
        all_max_pos = np.array([float('-inf')] * 3)
        
        for name, data in selected_bones:
            center = np.array(data['center']) * scale
            size = np.array(data['size']) * scale
            
            # Approximate rotation and direction for now (can be refined later)
            # For simplicity, assume identity rotation and Y-axis direction for now
            # This needs to be properly derived from bone transforms if used in optimization
            rotation_matrix = np.identity(3)
            direction_vector = np.array([0, 1, 0]) # Default to Y-axis
            
            bone_centers.append(center.astype(int).tolist())
            bone_sizes.append(size.astype(int).tolist())
            bone_rotations.append(rotation_matrix.flatten().astype(int).tolist()) # Flatten 3x3 to 9 elements
            bone_directions.append(direction_vector.astype(int).tolist())
            bone_names.append(name)
            
            # Update global min/max
            all_min_pos = np.minimum(all_min_pos, np.array(data['min_pos']) * scale)
            all_max_pos = np.maximum(all_max_pos, np.array(data['max_pos']) * scale)
            
        # Define max radius and length based on overall mesh size
        mesh_extent = all_max_pos - all_min_pos
        max_radius = int(np.max(mesh_extent) / 10) # 10% of largest extent
        max_length = int(np.max(mesh_extent) / 2)  # 50% of largest extent
        
        # Ensure min/max pos are integers
        min_pos_int = all_min_pos.astype(int).tolist()
        max_pos_int = all_max_pos.astype(int).tolist()

        try:
            with open(output_path, 'w') as f:
                f.write(f"n_capsules = {n_capsules};\n")
                f.write(f"bone_centers = {bone_centers};\n")
                f.write(f"bone_sizes = {bone_sizes};\n")
                f.write(f"bone_rotations = {bone_rotations};\n")
                f.write(f"bone_directions = {bone_directions};\n")
                f.write(f"bone_names = {json.dumps(bone_names)};\n")
                f.write(f"min_pos = {min_pos_int};\n")
                f.write(f"max_pos = {max_pos_int};\n")
                f.write(f"max_radius = {max_radius};\n")
                f.write(f"max_length = {max_length};\n")
            return True
        except Exception as e:
            print(f"Error generating MiniZinc data: {e}")
            return False

def main():
    """Test the MiniZinc data generator."""
    import sys
    from mesh_analyzer import MeshAnalyzer
    
    if len(sys.argv) != 3:
        print("Usage: python minizinc_data_generator.py <vrm_file> <output_dzn_file>")
        sys.exit(1)
    
    vrm_file = sys.argv[1]
    output_dzn_file = sys.argv[2]
    
    analyzer = MeshAnalyzer()
    if not analyzer.load_and_analyze(vrm_file):
        print("Failed to analyze VRM file.")
        sys.exit(1)
        
    bone_analysis = analyzer.get_bone_analysis()
    
    generator = MiniZincDataGenerator()
    if generator.generate_cpsat_data(output_dzn_file, bone_analysis, max_capsules=15, scale=1000):
        print(f"Successfully generated MiniZinc data to {output_dzn_file}")
    else:
        print("Failed to generate MiniZinc data.")
        sys.exit(1)

if __name__ == "__main__":
    main()
