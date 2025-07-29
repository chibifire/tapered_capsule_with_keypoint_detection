import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import csv

class CapsuleGenerator:
    def __init__(self, joint_names: List[str], bone_positions: Dict[str, np.ndarray], bone_rotations: Dict[str, np.ndarray], bone_directions: Dict[str, np.ndarray], vrm_humanoid_bones: Dict[str, str]):
        self.joint_names = joint_names
        self.bone_positions = bone_positions
        self.bone_rotations = bone_rotations
        self.bone_directions = bone_directions
        self.vrm_humanoid_bones = vrm_humanoid_bones

    def analyze_bone_geometry(self, vertices: List[List[float]], bone_weights: List[List[float]], bone_indices: List[List[int]]) -> Dict[str, Dict]:
        """Analyze geometry associated with each bone for capsule generation."""
        bone_geometry = {}
        
        if not vertices or not bone_weights:
            print("No vertex or weight data available")
            return bone_geometry
        
        # Group vertices by dominant bone influence
        for i, (vertex, weights, joints) in enumerate(zip(vertices, bone_weights, bone_indices)):
            if not weights or not joints:
                continue
                
            # Find dominant bone (highest weight)
            max_weight_idx = 0
            max_weight = weights[0]
            
            for j, weight in enumerate(weights):
                if weight > max_weight:
                    max_weight = weight
                    max_weight_idx = j
            
            if max_weight < 0.1:  # Skip vertices with very low bone influence
                continue
                
            bone_idx = joints[max_weight_idx]
            if bone_idx >= len(self.joint_names):
                continue
                
            bone_name = self.joint_names[bone_idx]
            
            if bone_name not in bone_geometry:
                bone_geometry[bone_name] = {
                    "vertices": [],
                    "weights": [],
                    "bounds": {"min": None, "max": None}
                }
            
            bone_geometry[bone_name]["vertices"].append(vertex)
            bone_geometry[bone_name]["weights"].append(max_weight)
        
        # Calculate bounds for each bone's geometry
        for bone_name, data in bone_geometry.items():
            if data["vertices"]:
                vertices_array = np.array(data["vertices"])
                data["bounds"]["min"] = np.min(vertices_array, axis=0).tolist()
                data["bounds"]["max"] = np.max(vertices_array, axis=0).tolist()
                data["center"] = ((np.array(data["bounds"]["min"]) + np.array(data["bounds"]["max"])) / 2).tolist()
                data["size"] = (np.array(data["bounds"]["max"]) - np.array(data["bounds"]["min"])).tolist()
        
        return bone_geometry

    def generate_capsule_constraints(self, bone_geometry: Dict[str, Dict], max_capsules: int = 25, integer_scale: int = None, fast_mode: bool = False) -> str:
        """Generate MiniZinc constraint data for capsule optimization.
        
        Args:
            bone_geometry: Analyzed bone geometry data
            max_capsules: Maximum number of capsules to generate
            integer_scale: If provided, scale float values to integers (e.g., 1000 for 1mm precision)
            fast_mode: If True, generate simplified data for fast optimization
        """
        if not bone_geometry:
            print("No bone geometry data available")
            return ""
        
        # Prioritize VRM humanoid bones, then fall back to high vertex count bones
        prioritized_bones = []
        remaining_bones = list(bone_geometry.items())
        
        # Define bone priority order for humanoid avatars (prioritize main body parts)
        priority_bones = [
            "hips", "spine", "chest", "upperChest", "neck", "head",
            "leftUpperArm", "leftLowerArm", "leftHand", 
            "rightUpperArm", "rightLowerArm", "rightHand",
            "leftUpperLeg", "leftLowerLeg", "leftFoot",
            "rightUpperLeg", "rightLowerLeg", "rightFoot",
            "leftShoulder", "rightShoulder", "leftThumbProximal", "rightThumbProximal",
            "leftIndexProximal", "rightIndexProximal", "leftMiddleProximal", "rightMiddleProximal"
        ]
        
        # Bones to deprioritize (clothing, accessories, etc.)
        deprioritized_patterns = [
            "skirt", "dress", "cloth", "hair", "accessory", "decoration",
            "PB_", "constraint", "helper", "IK", "pole", "target", "tail"
        ]
        
        # Core humanoid bone patterns to prioritize
        core_humanoid_patterns = [
            "hips", "spine", "chest", "neck", "head", "shoulder", "arm", "hand", "leg", "foot", "thigh", "calf"
        ]
        
        # First, add VRM humanoid bones in priority order
        if self.vrm_humanoid_bones:
            for priority_bone in priority_bones:
                if priority_bone in self.vrm_humanoid_bones:
                    vrm_node_name = self.vrm_humanoid_bones[priority_bone]
                    # Find this bone in our geometry analysis
                    for bone_name, bone_data in remaining_bones:
                        if bone_name == vrm_node_name and len(bone_data["vertices"]) > 10:  # Minimum vertex threshold
                            prioritized_bones.append((f"{priority_bone}({bone_name})", bone_data))
                            remaining_bones = [(n, d) for n, d in remaining_bones if n != bone_name]
                            break
        
        # Separate bones into categories
        core_humanoid_bones = []
        other_bones = []
        deprioritized_bones = []
        
        for bone_name, bone_data in remaining_bones:
            is_deprioritized = any(pattern.lower() in bone_name.lower() for pattern in deprioritized_patterns)
            is_core_humanoid = any(pattern.lower() in bone_name.lower() for pattern in core_humanoid_patterns)
            
            if is_deprioritized:
                deprioritized_bones.append((bone_name, bone_data))
            elif is_core_humanoid:
                core_humanoid_bones.append((bone_name, bone_data))
            else:
                other_bones.append((bone_name, bone_data))
        
        # Sort each category by vertex count (prioritize high mesh coverage)
        core_humanoid_bones.sort(key=lambda x: len(x[1]["vertices"]), reverse=True)
        other_bones.sort(key=lambda x: len(x[1]["vertices"]), reverse=True)
        deprioritized_bones.sort(key=lambda x: len(x[1]["vertices"]), reverse=True)
        
        # Fill remaining slots with core humanoid bones first
        for bone_name, bone_data in core_humanoid_bones:
            if len(prioritized_bones) >= max_capsules:
                break
            # Lower threshold for core humanoid bones
            if len(bone_data["vertices"]) > 20:
                prioritized_bones.append((bone_name, bone_data))
        
        # Then add other non-deprioritized bones
        for bone_name, bone_data in other_bones:
            if len(prioritized_bones) >= max_capsules:
                break
            # Higher threshold for other bones
            if len(bone_data["vertices"]) > 100:
                prioritized_bones.append((bone_name, bone_data))
        
        # If we still have slots and need more bones, add the best deprioritized ones
        if len(prioritized_bones) < max_capsules:
            deprioritized_bones = []
            for bone_name, bone_data in remaining_bones:
                is_deprioritized = any(pattern.lower() in bone_name.lower() for pattern in deprioritized_patterns)
                if is_deprioritized and len(bone_data["vertices"]) > 20:
                    deprioritized_bones.append((bone_name, bone_data))
            
            deprioritized_bones.sort(key=lambda x: len(x[1]["vertices"]), reverse=True)
            for bone_name, bone_data in deprioritized_bones:
                if len(prioritized_bones) >= max_capsules:
                    break
                prioritized_bones.append((bone_name, bone_data))
        
        significant_bones = prioritized_bones[:max_capsules]
        
        constraints = []
        if fast_mode:
            constraints.append(f"% Generated from VRM mesh analysis (FAST MODE)")
        else:
            constraints.append(f"% Generated from VRM mesh analysis")
        constraints.append(f"n_capsules = {len(significant_bones)};")
        constraints.append("")
        
        # Bone positions, rotations, directions, and geometry bounds
        bone_centers = []
        bone_sizes = []
        bone_rotations_list = []
        bone_directions_list = []
        bone_names_list = []
        
        for bone_name, data in significant_bones:
            center = data["center"]
            size = data["size"]
            
            bone_centers.append(f"[{center[0]:.6f}, {center[1]:.6f}, {center[2]:.6f}]")
            bone_sizes.append(f"[{size[0]:.6f}, {size[1]:.6f}, {size[2]:.6f}]")
            bone_names_list.append(f'"{bone_name}"')
            
            # Extract bone name from prioritized format
            actual_bone_name = bone_name.split('(')[-1].rstrip(')') if '(' in bone_name else bone_name
            
            # Get rotation matrix for this bone
            if actual_bone_name in self.bone_rotations:
                rot_matrix = self.bone_rotations[actual_bone_name]
                # Flatten 3x3 matrix to 9-element array for MiniZinc
                rot_flat = rot_matrix.flatten()
                rot_str = f"[{', '.join(f'{x:.6f}' for x in rot_flat)}]"
                bone_rotations_list.append(rot_str)
            else:
                # Default identity matrix if rotation not found
                identity = "[1.000000, 0.000000, 0.000000, 0.000000, 1.000000, 0.000000, 0.000000, 0.000000, 1.000000]"
                bone_rotations_list.append(identity)
            
            # Get bone direction vector for this bone
            if actual_bone_name in self.bone_directions:
                direction = self.bone_directions[actual_bone_name]
                dir_str = f"[{direction[0]:.6f}, {direction[1]:.6f}, {direction[2]:.6f}]"
                bone_directions_list.append(dir_str)
            else:
                # Default Y-axis direction if no direction found (vertical capsule)
                default_direction = "[0.000000, 1.000000, 0.000000]"
                bone_directions_list.append(default_direction)
        
        # Generate data arrays - either float or integer based on scaling
        if integer_scale:
            # Integer scaling for CP-SAT
            constraints.append(f"% Integer scaling factor: {integer_scale} (1 unit = {1.0/integer_scale:.3f} meters)")
            
            # Scale bone centers and sizes to integers
            bone_centers_scaled = []
            bone_sizes_scaled = []
            for _, data in significant_bones:
                center = data["center"]
                size = data["size"]
                bone_centers_scaled.extend([int(center[0] * integer_scale), int(center[1] * integer_scale), int(center[2] * integer_scale)])
                bone_sizes_scaled.extend([int(size[0] * integer_scale), int(size[1] * integer_scale), int(size[2] * integer_scale)])
            
            constraints.append(f"bone_centers = array2d(1..{len(significant_bones)}, 1..3, [" + ", ".join(map(str, bone_centers_scaled)) + "]);")
            constraints.append(f"bone_sizes = array2d(1..{len(significant_bones)}, 1..3, [" + ", ".join(map(str, bone_sizes_scaled)) + "]);")
            
            # Bone rotations remain as scaled integers (multiply by 1000 for precision)
            bone_rotations_flat = []
            for bone_name, data in significant_bones:
                actual_bone_name = bone_name.split('(')[-1].rstrip(')') if '(' in bone_name else bone_name
                
                if actual_bone_name in self.bone_rotations:
                    rot_matrix = self.bone_rotations[actual_bone_name]
                    rot_flat = rot_matrix.flatten()
                    bone_rotations_flat.extend([int(x * 1000) for x in rot_flat])  # Scale rotations by 1000
                else:
                    # Default identity matrix scaled
                    bone_rotations_flat.extend([1000, 0, 0, 0, 1000, 0, 0, 0, 1000])
            
            constraints.append(f"bone_rotations = array2d(1..{len(significant_bones)}, 1..9, [" + ", ".join(map(str, bone_rotations_flat)) + "]);")
            
            # Bone directions as scaled integers (multiply by 1000 for precision)
            bone_directions_flat = []
            for bone_name, data in significant_bones:
                actual_bone_name = bone_name.split('(')[-1].rstrip(')') if '(' in bone_name else bone_name
                
                if actual_bone_name in self.bone_directions:
                    direction = self.bone_directions[actual_bone_name]
                    bone_directions_flat.extend([int(direction[0] * 1000), int(direction[1] * 1000), int(direction[2] * 1000)])
                else:
                    # Default Y-axis direction scaled
                    bone_directions_flat.extend([0, 1000, 0])
            
            constraints.append(f"bone_directions = array2d(1..{len(significant_bones)}, 1..3, [" + ", ".join(map(str, bone_directions_flat)) + "]);")
            
        else:
            # Float format for Gecode
            constraints.append(f"bone_centers = array2d(1..{len(significant_bones)}, 1..3, [" + ", ".join([f"{center[0]:.6f}, {center[1]:.6f}, {center[2]:.6f}" for _, data in significant_bones for center in [data["center"]]]) + "]);")
            constraints.append(f"bone_sizes = array2d(1..{len(significant_bones)}, 1..3, [" + ", ".join([f"{size[0]:.6f}, {size[1]:.6f}, {size[2]:.6f}" for _, data in significant_bones for size in [data["size"]]]) + "]);")
            
            # Generate bone rotations as flat array with floats
            bone_rotations_flat = []
            for bone_name, data in significant_bones:
                actual_bone_name = bone_name.split('(')[-1].rstrip(')') if '(' in bone_name else bone_name
                
                if actual_bone_name in self.bone_rotations:
                    rot_matrix = self.bone_rotations[actual_bone_name]
                    rot_flat = rot_matrix.flatten()
                    bone_rotations_flat.extend([f'{x:.6f}' for x in rot_flat])
                else:
                    # Default identity matrix if rotation not found
                    bone_rotations_flat.extend(["1.000000", "0.000000", "0.000000", "0.000000", "1.000000", "0.000000", "0.000000", "0.000000", "1.000000"])
            
            constraints.append(f"bone_rotations = array2d(1..{len(significant_bones)}, 1..9, [" + ", ".join(bone_rotations_flat) + "]);")
            
            # Generate bone directions as flat array with floats
            bone_directions_flat = []
            for bone_name, data in significant_bones:
                actual_bone_name = bone_name.split('(')[-1].rstrip(')') if '(' in bone_name else bone_name
                
                if actual_bone_name in self.bone_directions:
                    direction = self.bone_directions[actual_bone_name]
                    bone_directions_flat.extend([f'{direction[0]:.6f}', f'{direction[1]:.6f}', f'{direction[2]:.6f}'])
                else:
                    # Default Y-axis direction if no direction found
                    bone_directions_flat.extend(["0.000000", "1.000000", "0.000000"])
            
            constraints.append(f"bone_directions = array2d(1..{len(significant_bones)}, 1..3, [" + ", ".join(bone_directions_flat) + "]);")
        
        constraints.append(f"bone_names = [" + ", ".join(bone_names_list) + "];")
        constraints.append("")
        
        # Skip hierarchy data completely - capsules will only use weight painting
        constraints.append(f"% No bone hierarchy - capsules use weight painting only")
        constraints.append("")
        
        # Calculate reasonable bounds for capsule parameters
        all_vertices = np.array([v for data in bone_geometry.values() for v in data["vertices"]])
        if len(all_vertices) > 0:
            global_min = np.min(all_vertices, axis=0)
            global_max = np.max(all_vertices, axis=0)
            global_size = global_max - global_min
            
            # Reasonable parameter bounds
            max_radius = max(global_size) * 0.3
            max_length = max(global_size) * 0.8
            
            if integer_scale:
                # Integer bounds for CP-SAT
                constraints.append(f"% Global mesh bounds (scaled)")
                constraints.append(f"min_pos = [{int(global_min[0] * integer_scale)}, {int(global_min[1] * integer_scale)}, {int(global_min[2] * integer_scale)}];")
                constraints.append(f"max_pos = [{int(global_max[0] * integer_scale)}, {int(global_max[1] * integer_scale)}, {int(global_max[2] * integer_scale)}];")
                constraints.append(f"max_radius = {int(max_radius * integer_scale)};")
                constraints.append(f"max_length = {int(max_length * integer_scale)};")
            else:
                # Float bounds for Gecode
                constraints.append(f"% Global mesh bounds")
                constraints.append(f"min_pos = [{global_min[0]:.6f}, {global_min[1]:.6f}, {global_min[2]:.6f}];")
                constraints.append(f"max_pos = [{global_max[0]:.6f}, {global_max[1]:.6f}, {global_max[2]:.6f}];")
                constraints.append(f"max_radius = {max_radius:.6f};")
                constraints.append(f"max_length = {max_length:.6f};")
        
        return "\n".join(constraints)
    
    def save_analysis_data(self, output_path: str, integer_scale: int = None):
        """Save analysis data to DZN file for MiniZinc.
        
        Args:
            output_path: Output file path
            integer_scale: If provided, scale float values to integers (e.g., 1000 for 1mm precision)
        """
        constraints = self.generate_capsule_constraints(integer_scale=integer_scale)
        
        if constraints:
            with open(output_path, 'w') as f:
                f.write(constraints)
            print(f"Saved analysis data to: {output_path}")
            if integer_scale:
                print(f"Integer scaling: {integer_scale}x (1 unit = {1.0/integer_scale:.3f} meters)")
            return True
        else:
            print("No data to save")
            return False
    
    def save_gecode_data(self, output_path: str, max_capsules: int = 25):
        """Save float data for Gecode solver.
        
        Args:
            output_path: Output file path
            max_capsules: Maximum number of capsules
        """
        constraints = self.generate_capsule_constraints(max_capsules=max_capsules)
        
        if constraints:
            with open(output_path, 'w') as f:
                f.write(constraints)
            print(f"Saved analysis data to: {output_path}")
            print(f"Using float values (no scaling)")
            return True
        else:
            print("No data to save")
            return False
    
    def export_cpsat_results_to_json(self, results_file: str, output_file: str, scale: int = 1000):
        """Parse CP-SAT results and export to JSON format.
        
        Args:
            results_file: Path to CP-SAT results file
            output_file: Output JSON file path
            scale: Integer scaling factor used in optimization
        """
        try:
            with open(results_file, 'r') as f:
                content = f.read()
            
            capsules = []
            lines = content.split('\n')
            
            for line in lines:
                if line.startswith('Capsule ') and 'pos(' in line:
                    # Parse capsule data
                    parts = line.split()
                    capsule_id = int(parts[1].rstrip(':'))
                    
                    # Extract position
                    pos_start = line.find('pos(') + 4
                    pos_end = line.find(')', pos_start)
                    pos_str = line[pos_start:pos_end]
                    pos_values = [int(x) / scale for x in pos_str.split(',')]
                    
                    # Extract length
                    len_start = line.find('len(') + 4
                    len_end = line.find(')', len_start)
                    length = int(line[len_start:len_end]) / scale
                    
                    # Extract radii
                    radii_start = line.find('radii(') + 6
                    radii_end = line.find(')', radii_start)
                    radii_str = line[radii_start:radii_end]
                    radii = [int(x) / scale for x in radii_str.split(',')]
                    
                    # Extract bone name
                    bone_start = line.find('bone(') + 5
                    bone_end = line.find(')', bone_start)
                    bone_name = line[bone_start:bone_end]
                    
                    capsule_data = {
                        "id": capsule_id,
                        "position": {"x": pos_values[0], "y": pos_values[1], "z": pos_values[2]},
                        "length": length,
                        "radius_top": radii[0],
                        "radius_bottom": radii[1],
                        "bone_name": bone_name
                    }
                    capsules.append(capsule_data)
            
            # Extract summary statistics
            active_count = 0
            size_coverage = 0
            bone_coverage = 0
            overlap_penalty = 0
            
            for line in lines:
                if "Active capsules:" in line:
                    active_count = int(line.split()[2].split('/')[0])
                elif "Size coverage:" in line:
                    size_coverage = int(line.split()[2])
                elif "Bone coverage:" in line:
                    bone_coverage = int(line.split()[2])
                elif "Overlap penalty:" in line:
                    overlap_penalty = int(line.split()[2])
            
            result_data = {
                "metadata": {
                    "solver": "OR-Tools CP-SAT",
                    "scaling_factor": scale,
                    "precision_mm": 1000 / scale,
                    "total_capsules": len(capsules),
                    "active_capsules": active_count
                },
                "statistics": {
                    "size_coverage": size_coverage,
                    "bone_coverage": bone_coverage,
                    "overlap_penalty": overlap_penalty
                },
                "capsules": capsules
            }
            
            with open(output_file, 'w') as f:
                import json
                json.dump(result_data, f, indent=2)
            
            print(f"Exported CP-SAT results to JSON: {output_file}")
            return True
            
        except Exception as e:
            print(f"Error exporting CP-SAT results: {e}")
            return False
    
    def export_cpsat_results_to_csv(self, results_file: str, output_file: str, scale: int = 1000):
        """Parse CP-SAT results and export to CSV format.
        
        Args:
            results_file: Path to CP-SAT results file
            output_file: Output CSV file path
            scale: Integer scaling factor used in optimization
        """
        try:
            with open(results_file, 'r') as f:
                content = f.read()
            
            import csv
            
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = ['capsule_id', 'pos_x', 'pos_y', 'pos_z', 'length', 'radius_top', 'radius_bottom', 'bone_name']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('Capsule ') and 'pos(' in line:
                        # Parse capsule data
                        parts = line.split()
                        capsule_id = int(parts[1].rstrip(':'))
                        
                        # Extract position
                        pos_start = line.find('pos(') + 4
                        pos_end = line.find(')', pos_start)
                        pos_str = line[pos_start:pos_end]
                        pos_values = [int(x) / scale for x in pos_str.split(',')]
                        
                        # Extract length
                        len_start = line.find('len(') + 4
                        len_end = line.find(')', len_start)
                        length = int(line[len_start:len_end]) / scale
                        
                        # Extract radii
                        radii_start = line.find('radii(') + 6
                        radii_end = line.find(')', radii_start)
                        radii_str = line[radii_start:radii_end]
                        radii = [int(x) / scale for x in radii_str.split(',')]
                        
                        # Extract bone name
                        bone_start = line.find('bone(') + 5
                        bone_end = line.find(')', bone_start)
                        bone_name = line[bone_start:bone_end]
                        
                        writer.writerow({
                            'capsule_id': capsule_id,
                            'pos_x': pos_values[0],
                            'pos_y': pos_values[1],
                            'pos_z': pos_values[2],
                            'length': length,
                            'radius_top': radii[0],
                            'radius_bottom': radii[1],
                            'bone_name': bone_name
                        })
            
            print(f"Exported CP-SAT results to CSV: {output_file}")
            return True
            
        except Exception as e:
            print(f"Error exporting CP-SAT results to CSV: {e}")
            return False
    
    def print_analysis_summary(self, vertices, triangles, normals, mesh_bounds):
        """Print summary of the mesh analysis."""
        print(f"\nVRM Mesh Analysis Summary:")
        print(f"Total vertices: {len(vertices)}")
        print(f"Total triangles: {len(triangles)}")
        print(f"Total normals: {len(normals)}")
        print(f"Total joints: {len(self.joint_names)}")
        print(f"Meshes analyzed: {len(mesh_bounds)}")
        
        # Show triangle mesh data per mesh
        total_surface_area = 0.0
        print(f"\nTriangle Mesh Data:")
        for mesh_name, bounds in mesh_bounds.items():
            surface_area = bounds.get('surface_area', 0.0)
            total_surface_area += surface_area
            print(f"  {mesh_name}: {bounds['vertex_count']} vertices, "
                  f"{bounds['triangle_count']} triangles, "
                  f"surface_area={surface_area:.6f}")
        
        print(f"Total surface area: {total_surface_area:.6f}")
        
        bone_geometry = self.analyze_bone_geometry(vertices, [], [])  # Simplified call
        print(f"\nBone geometry analysis (with triangle mesh support):")
        
        # Sort by vertex count
        sorted_bones = sorted(
            bone_geometry.items(),
            key=lambda x: len(x[1]["vertices"]),
            reverse=True
        )
        
        for bone_name, data in sorted_bones[:10]:  # Top 10 bones
            vertex_count = len(data["vertices"])
            if vertex_count > 0:
                center = data["center"]
                size = data["size"]
                print(f"  {bone_name}: {vertex_count} vertices, "
                      f"center=({center[0]:.3f},{center[1]:.3f},{center[2]:.3f}), "
                      f"size=({size[0]:.3f},{size[1]:.3f},{size[2]:.3f})")
