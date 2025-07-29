#!/usr/bin/env python3
"""
CoACD-based Tapered Capsule Optimization Pipeline.
Implements the algorithm described in docs/tapered_capsule_optimization_algorithm.md
"""

import os
import sys
import subprocess
import tempfile
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Any
from sklearn.decomposition import PCA

class CoACDCapsulePipeline:
    """Pipeline for generating optimized tapered capsules using CoACD decomposition."""
    
    def __init__(self, vrm_path: str, output_dir: str = None):
        self.vrm_path = Path(vrm_path)
        self.output_dir = Path(output_dir) if output_dir else self.vrm_path.parent
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_files = []
        self.skeleton_data = None
        self.joint_hierarchy = {}
        self.bone_parent_map = {}
        self.bone_weights = None
        self.bone_indices = None
        self.joint_names = []
        self.bone_vertex_groups = {}
        
    def __del__(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except:
                pass
    
    def load_mesh_data(self) -> bool:
        """Step 1: Load input mesh using existing GLTF parser."""
        try:
            print("Step 1: Loading mesh with GLTF parser")
            
            # Use existing GLTF parser
            from gltf_parser import GLTFParser
            from mesh_data_extractor import MeshDataExtractor
            
            # Load GLTF data
            self.gltf_parser = GLTFParser()
            if not self.gltf_parser.load_glb(str(self.vrm_path)):
                print("Error: Failed to load GLTF file")
                return False
            
            gltf_data = self.gltf_parser.get_gltf_data()
            print(f"  Loaded GLTF with {len(gltf_data.get('meshes', []))} meshes")
            
            # Extract mesh data
            self.mesh_data_extractor = MeshDataExtractor(gltf_data, self.gltf_parser.get_accessor_data)
            self.mesh_data_extractor.extract_mesh_data()
            
            # Extract skeleton and bone weight data
            self._extract_skeleton_data_from_gltf(gltf_data)
            
            return True
        except Exception as e:
            print(f"Error loading mesh: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_skeleton_data_from_gltf(self, gltf_data: Dict[str, Any]):
        """Extract skeleton and bone weight data from GLTF data."""
        try:
            # Extract joint names from nodes
            if "nodes" in gltf_data:
                # For VRM, joints are typically in the skins section
                if "skins" in gltf_data and gltf_data["skins"]:
                    skin = gltf_data["skins"][0]  # Use first skin
                    if "joints" in skin:
                        joint_indices = skin["joints"]
                        self.joint_names = [gltf_data["nodes"][idx]["name"] for idx in joint_indices 
                                          if idx < len(gltf_data["nodes"]) and "name" in gltf_data["nodes"][idx]]
                        print(f"  Found {len(self.joint_names)} joints in skin")
                
                # Fallback: use all node names
                if not self.joint_names:
                    self.joint_names = [node["name"] for node in gltf_data["nodes"] if "name" in node]
                    print(f"  Found {len(self.joint_names)} joints in nodes")
            
            # Extract bone weights and indices from mesh data extractor
            if hasattr(self, 'mesh_data_extractor'):
                self.bone_weights = self.mesh_data_extractor.get_bone_weights()
                self.bone_indices = self.mesh_data_extractor.get_bone_indices()
                print(f"  Extracted bone weights for {len(self.bone_weights)} vertices")
            
            # Group vertices by dominant bone influence
            self._group_vertices_by_bone()
            
        except Exception as e:
            print(f"  Warning: Could not extract skeleton data: {e}")
            import traceback
            traceback.print_exc()
    
    def _group_vertices_by_bone(self):
        """Group vertices by their dominant bone influence."""
        if self.bone_weights is None or self.bone_indices is None:
            print("  No bone weight data available for vertex grouping")
            return
        
        print("  Grouping vertices by dominant bone influence")
        
        # For each vertex, find the bone with the highest weight
        for i, (weights, indices) in enumerate(zip(self.bone_weights, self.bone_indices)):
            if len(weights) == 0 or len(indices) == 0:
                continue
                
            # Find the bone with maximum weight
            max_weight_idx = 0
            max_weight = weights[0]
            
            for j, weight in enumerate(weights):
                if weight > max_weight:
                    max_weight = weight
                    max_weight_idx = j
            
            # Skip vertices with very low bone influence
            if max_weight < 0.1:
                continue
                
            bone_idx = int(indices[max_weight_idx])
            
            if bone_idx >= len(self.joint_names):
                continue
                
            bone_name = self.joint_names[bone_idx]
            
            # Add vertex to bone group
            if bone_name not in self.bone_vertex_groups:
                self.bone_vertex_groups[bone_name] = []
            
            self.bone_vertex_groups[bone_name].append(i)
        
        print(f"  Grouped vertices into {len(self.bone_vertex_groups)} bone groups")
        for bone_name, vertex_indices in list(self.bone_vertex_groups.items())[:5]:
            print(f"    {bone_name}: {len(vertex_indices)} vertices")
        if len(self.bone_vertex_groups) > 5:
            print(f"    ... and {len(self.bone_vertex_groups) - 5} more bones")
    
    def run_coacd_decomposition(self, mesh: Any, threshold: float = 0.05) -> List[Any]:
        """Step 2: Run coacd to break mesh into convex hulls."""
        # If we have bone vertex groups, run CoACD per bone
        if self.bone_vertex_groups:
            return self._run_coacd_per_bone(mesh, threshold)
        else:
            # Fallback to global CoACD if no bone data available
            return self._run_coacd_global(mesh, threshold)
    
    def _run_coacd_global(self, mesh: Any, threshold: float = 0.05) -> List[Any]:
        """Run CoACD on the entire mesh as a single piece."""
        try:
            import coacd
            print("Step 2: Running global CoACD decomposition")
            
            # Convert mesh to format expected by coacd
            vertices = np.array(mesh.vertices)
            
            # Check if we have enough vertices for meaningful decomposition
            if len(vertices) < 4:
                print("  Skipping global CoACD: insufficient vertices")
                return []
            
            faces = np.array([])  # No faces for point cloud approach
            
            # Create CoACD mesh directly from vertices and empty faces (point cloud)
            # CoACD requires faces to be a 2D array with shape (n, 3)
            coacd_mesh = coacd.Mesh(vertices, faces.reshape(0, 3))
            
            try:
                parts = coacd.run_coacd(
                    mesh=coacd_mesh,
                    threshold=threshold,
                    max_convex_hull=64,
                    preprocess_mode="auto",
                    preprocess_resolution=50,
                    resolution=100,
                    mcts_nodes=20,
                    mcts_iterations=150,
                    mcts_max_depth=30,
                    pca=0,  # Changed from False to 0 (int)
                    merge=False,
                    decimate=False,
                    max_ch_vertex=256,
                    extrude=False,
                )
            except Exception as coacd_error:
                print(f"  CoACD failed for global mesh, creating simple convex hull: {coacd_error}")
                # Create a single convex hull from all vertices as fallback
                parts = [(vertices, np.array([]).reshape(0, 3))]
            
            # Convert to custom hull objects
            hulls = []
            for i, (part_vertices, part_faces) in enumerate(parts):
                hull = {
                    'vertices': part_vertices,
                    'faces': part_faces
                }
                hulls.append(hull)
            
            print(f"  Generated {len(hulls)} convex hulls")
            return hulls
        except ImportError:
            print("Error: coacd not installed. Please install with 'pip install coacd'")
            return []
        except Exception as e:
            print(f"Error running CoACD: {e}")
            return []
    
    def _run_coacd_per_bone(self, mesh: Any, threshold: float = 0.05) -> List[Any]:
        """Run CoACD separately on each bone's vertex set."""
        try:
            import coacd
            print("Step 2: Running per-bone CoACD decomposition")
            
            all_hulls = []
            bone_count = 0
            
            # Process bones in hierarchical order (parents before children)
            # For now, we'll process all bones, but in a more sophisticated implementation
            # we would sort by hierarchy depth
            for bone_name, vertex_indices in self.bone_vertex_groups.items():
                # Skip bones with too few vertices
                if len(vertex_indices) < 10:
                    print(f"  Skipping {bone_name}: only {len(vertex_indices)} vertices")
                    continue
                
                print(f"  Processing {bone_name}: {len(vertex_indices)} vertices")
                
                # Extract vertices for this bone
                bone_vertices = np.array([mesh.vertices[i] for i in vertex_indices])
                
                # Create a temporary mesh with just these vertices
                # This is a simplified approach - in practice, we'd want to maintain
                # proper connectivity information
                
                # For now, we'll create a point cloud and run CoACD on it
                # This is not ideal, but demonstrates the concept
                
                # Run CoACD decomposition on bone vertices
                try:
                    # Check if we have enough vertices for meaningful decomposition
                    if len(bone_vertices) < 4:
                        print(f"    Skipping {bone_name}: insufficient vertices ({len(bone_vertices)} < 4)")
                        continue
                    
                    # Try to create a simple convex hull as a fallback when CoACD fails
                    try:
                        # Create CoACD mesh directly from vertices and empty faces (point cloud)
                        # CoACD requires faces to be a 2D array with shape (n, 3)
                        coacd_mesh = coacd.Mesh(bone_vertices, np.array([]).reshape(0, 3))
                        
                        parts = coacd.run_coacd(
                            mesh=coacd_mesh,
                            threshold=threshold,
                            max_convex_hull=16,  # Fewer hulls per bone
                            preprocess_mode="auto",
                            preprocess_resolution=30,
                            resolution=50,
                            mcts_nodes=10,
                            mcts_iterations=100,
                            mcts_max_depth=20,
                            pca=0,  # Changed from False to 0 (int)
                            merge=False,
                            decimate=False,
                            max_ch_vertex=128,
                            extrude=False,
                        )
                    except Exception as coacd_error:
                        print(f"    CoACD failed for {bone_name}, creating simple convex hull: {coacd_error}")
                        # Create a single convex hull from all vertices as fallback
                        parts = [(bone_vertices, np.array([]).reshape(0, 3))]
                    
                    # Convert to custom hull objects with bone association
                    bone_hulls = []
                    for i, (part_vertices, part_faces) in enumerate(parts):
                        hull = {
                            'vertices': part_vertices,
                            'faces': part_faces,
                            'metadata': {'bone_name': bone_name}
                        }
                        bone_hulls.append(hull)
                    
                    print(f"    Generated {len(bone_hulls)} convex hulls for {bone_name}")
                    all_hulls.extend(bone_hulls)
                    bone_count += 1
                    
                except Exception as e:
                    print(f"    Warning: Failed to process {bone_name}: {e}")
                    continue
            
            print(f"  Processed {bone_count} bones, generated {len(all_hulls)} total convex hulls")
            return all_hulls
            
        except ImportError:
            print("Error: coacd not installed. Please install with 'pip install coacd'")
            return []
        except Exception as e:
            print(f"Error running per-bone CoACD: {e}")
            return []
    
    def generate_candidate_capsules(self, hulls: List[Any]) -> List[Dict[str, Any]]:
        """Step 3: Generate candidate capsules from convex hulls."""
        print("Step 3: Generating candidate capsules")
        
        capsules = []
        for i, hull in enumerate(hulls):
            try:
                # Apply PCA to find longest axis (capsule orientation)
                pca = PCA(n_components=3)
                pca.fit(hull['vertices'])
                
                # Principal axis is the first component
                principal_axis = pca.components_[0]
                
                # Project vertices onto principal axis to find endpoints
                projections = np.dot(hull['vertices'], principal_axis)
                min_idx = np.argmin(projections)
                max_idx = np.argmax(projections)
                
                p1 = hull['vertices'][min_idx]  # Endpoint 1
                p2 = hull['vertices'][max_idx]  # Endpoint 2
                
                # Calculate height as distance between endpoints
                height = np.linalg.norm(p2 - p1)
                
                # Calculate radii from vertex extents perpendicular to axis
                # Project vertices onto plane perpendicular to principal axis
                center = (p1 + p2) / 2
                direction = (p2 - p1) / height if height > 0 else np.array([0, 1, 0])
                
                # Calculate distances from axis for all vertices
                distances = []
                for vertex in hull['vertices']:
                    # Vector from p1 to vertex
                    to_vertex = vertex - p1
                    # Project onto direction vector
                    projection_length = np.dot(to_vertex, direction)
                    # Point on axis closest to vertex
                    closest_point = p1 + projection_length * direction
                    # Distance from vertex to axis
                    distance = np.linalg.norm(vertex - closest_point)
                    distances.append(distance)
                
                # Use percentiles for more robust radius estimation
                distances = np.array(distances)
                radius_top = np.percentile(distances, 90)  # 90th percentile
                radius_bottom = np.percentile(distances, 90)  # Same for now, could be different
                
                # Calculate capsule center
                capsule_center = (p1 + p2) / 2
                
                # For swing and twist rotation, we'll use the principal axis
                # In a more sophisticated implementation, we'd calculate these from bone data
                swing_rotation = principal_axis  # Simplified representation
                twist_rotation = 0.0  # Simplified representation
                
                # Extract bone name if available
                bone_name = f"Capsule_{i}"
                if 'metadata' in hull and 'bone_name' in hull['metadata']:
                    bone_name = hull['metadata']['bone_name']
                
                capsule = {
                    'id': i,
                    'hull': hull,
                    'center': capsule_center.tolist(),
                    'p1': p1.tolist(),
                    'p2': p2.tolist(),
                    'height': float(height),
                    'radius_top': float(radius_top),
                    'radius_bottom': float(radius_bottom),
                    'principal_axis': principal_axis.tolist(),
                    'swing_rotation': swing_rotation.tolist(),
                    'twist_rotation': float(twist_rotation),
                    'bone_name': bone_name
                }
                
                capsules.append(capsule)
                print(f"  Capsule {i} ({bone_name}): height={height:.3f}, radii=({radius_top:.3f},{radius_bottom:.3f})")
                
            except Exception as e:
                print(f"  Error generating capsule {i}: {e}")
                continue
        
        print(f"  Generated {len(capsules)} candidate capsules")
        return capsules
    
    def sample_witness_points(self, mesh: Any, num_points: int = 5000) -> np.ndarray:
        """Step 4: Sample witness points from mesh interior."""
        print("Step 4: Sampling witness points")
        
        try:
            # Sample points from the mesh surface
            points, face_indices = mesh.sample(num_points, return_index=True)
            
            # For interior points, we could sample within the mesh volume
            # For now, we'll use surface points as a simplification
            # In a more sophisticated implementation, we'd use raycasting or other methods
            
            print(f"  Sampled {len(points)} witness points")
            return points
        except Exception as e:
            print(f"  Error sampling witness points: {e}")
            # Fallback to uniform sampling within mesh bounds
            bounds = mesh.bounds
            points = np.random.uniform(bounds[0], bounds[1], (num_points, 3))
            print(f"  Sampled {len(points)} witness points (fallback method)")
            return points
    
    def build_coverage_matrix(self, capsules: List[Dict[str, Any]], witness_points: np.ndarray) -> np.ndarray:
        """Step 5: Build coverage matrix."""
        print("Step 5: Building coverage matrix")
        
        num_capsules = len(capsules)
        num_points = len(witness_points)
        
        # Initialize coverage matrix
        coverage_matrix = np.zeros((num_capsules, num_points), dtype=bool)
        
        # Check which capsules contain which points using capsule-based checking
        for i, capsule in enumerate(capsules):
            p1 = np.array(capsule['p1'])
            p2 = np.array(capsule['p2'])
            radius_top = capsule['radius_top']
            radius_bottom = capsule['radius_bottom']
            
            for j, point in enumerate(witness_points):
                # Check if point is inside the tapered capsule
                if self._point_in_tapered_capsule(point, p1, p2, radius_top, radius_bottom):
                    coverage_matrix[i, j] = True
        
        print(f"  Built {num_capsules}x{num_points} coverage matrix")
        print(f"  Total covered points: {np.sum(np.any(coverage_matrix, axis=0))}/{num_points}")
        return coverage_matrix
    
    def _point_to_line_segment_distance(self, point: np.ndarray, p1: np.ndarray, p2: np.ndarray) -> float:
        """Calculate distance from point to line segment."""
        # Vector from p1 to p2
        line_vec = p2 - p1
        line_len = np.linalg.norm(line_vec)
        
        if line_len < 1e-8:
            return np.linalg.norm(point - p1)
        
        # Normalize line vector
        line_unit = line_vec / line_len
        
        # Vector from p1 to point
        point_vec = point - p1
        
        # Project point_vec onto line_vec
        projection_length = np.dot(point_vec, line_unit)
        
        # Clamp projection to line segment
        projection_length = np.clip(projection_length, 0, line_len)
        
        # Closest point on line segment
        closest_point = p1 + projection_length * line_unit
        
        # Distance from point to closest point
        return np.linalg.norm(point - closest_point)
    
    def _point_in_tapered_capsule(self, point: np.ndarray, p1: np.ndarray, p2: np.ndarray, 
                                 radius_top: float, radius_bottom: float) -> bool:
        """Check if a point is inside a tapered capsule defined by two endpoints and radii."""
        # Vector from p1 to p2
        line_vec = p2 - p1
        line_len = np.linalg.norm(line_vec)
        
        if line_len < 1e-8:
            # Degenerate case - treat as sphere
            return np.linalg.norm(point - p1) <= max(radius_top, radius_bottom)
        
        # Normalize line vector
        line_unit = line_vec / line_len
        
        # Vector from p1 to point
        point_vec = point - p1
        
        # Project point_vec onto line_vec
        projection_length = np.dot(point_vec, line_unit)
        
        # Clamp projection to line segment
        projection_length = np.clip(projection_length, 0, line_len)
        
        # Closest point on line segment
        closest_point = p1 + projection_length * line_unit
        
        # Distance from point to closest point on line segment
        distance_to_axis = np.linalg.norm(point - closest_point)
        
        # Interpolate radius at this point along the capsule
        t = projection_length / line_len if line_len > 0 else 0
        current_radius = radius_bottom + t * (radius_top - radius_bottom)
        
        # Point is inside if distance to axis is less than or equal to current radius
        return distance_to_axis <= current_radius
    
    def create_minizinc_data_file(self, capsules: List[Dict[str, Any]], 
                                 witness_points: np.ndarray, 
                                 coverage_matrix: np.ndarray,
                                 output_path: str) -> bool:
        """Step 6: Create MiniZinc data file."""
        print("Step 6: Creating MiniZinc data file")
        
        try:
            with open(output_path, 'w') as f:
                # Write problem dimensions
                f.write(f"num_capsules = {len(capsules)};\n")
                f.write(f"num_points = {len(witness_points)};\n")
                f.write("\n")
                
                # Write capsule parameters
                f.write("% Capsule parameters\n")
                centers = [f"[{c['center'][0]:.6f}, {c['center'][1]:.6f}, {c['center'][2]:.6f}]" for c in capsules]
                f.write(f"capsule_centers = array2d(1..{len(capsules)}, 1..3, [{', '.join(centers)}]);\n")
                
                heights = [f"{c['height']:.6f}" for c in capsules]
                f.write(f"capsule_heights = [{', '.join(heights)}];\n")
                
                radii_top = [f"{c['radius_top']:.6f}" for c in capsules]
                f.write(f"capsule_radii_top = [{', '.join(radii_top)}];\n")
                
                radii_bottom = [f"{c['radius_bottom']:.6f}" for c in capsules]
                f.write(f"capsule_radii_bottom = [{', '.join(radii_bottom)}];\n")
                
                # Write swing and twist rotations
                swing_rotations = []
                for c in capsules:
                    swing = c['swing_rotation']
                    swing_rotations.append(f"[{swing[0]:.6f}, {swing[1]:.6f}, {swing[2]:.6f}]")
                f.write(f"capsule_swing_rotations = array2d(1..{len(capsules)}, 1..3, [{', '.join(swing_rotations)}]);\n")
                
                twist_rotations = [f"{c['twist_rotation']:.6f}" for c in capsules]
                f.write(f"capsule_twist_rotations = [{', '.join(twist_rotations)}];\n")
                f.write("\n")
                
                # Write witness points
                f.write("% Witness points\n")
                points_list = []
                for point in witness_points:
                    points_list.append(f"[{point[0]:.6f}, {point[1]:.6f}, {point[2]:.6f}]")
                f.write(f"witness_points = array2d(1..{len(witness_points)}, 1..3, [{', '.join(points_list)}]);\n")
                f.write("\n")
                
                # Write coverage matrix (as a flattened array)
                f.write("% Coverage matrix\n")
                coverage_flat = coverage_matrix.flatten().astype(int).tolist()
                f.write(f"coverage_matrix = array2d(1..{len(capsules)}, 1..{len(witness_points)}, [{', '.join(map(str, coverage_flat))}]);\n")
            
            print(f"  Created MiniZinc data file: {output_path}")
            return True
        except Exception as e:
            print(f"  Error creating MiniZinc data file: {e}")
            return False
    
    def run_minizinc_optimization(self, model_path: str, data_path: str, output_path: str) -> bool:
        """Step 7: Run MiniZinc optimization."""
        print("Step 7: Running MiniZinc optimization")
        
        try:
            # Run MiniZinc solver
            cmd = [
                "minizinc",
                "--solver", "gecode",
                "--all-solutions",
                "--output-mode", "json",
                "-o", output_path,
                model_path,
                data_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"  Optimization completed successfully")
                print(f"  Results saved to: {output_path}")
                return True
            else:
                print(f"  Optimization failed with return code {result.returncode}")
                print(f"  Error: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("  Optimization timed out")
            return False
        except FileNotFoundError:
            print("  Error: MiniZinc not found. Please install MiniZinc.")
            return False
        except Exception as e:
            print(f"  Error running MiniZinc: {e}")
            return False
    
    def process_results(self, capsules: List[Dict[str, Any]], 
                       results_path: str, 
                       output_gltf_path: str) -> bool:
        """Step 8: Process optimization results."""
        print("Step 8: Processing optimization results")
        
        try:
            # Read results
            with open(results_path, 'r') as f:
                results_content = f.read()
            
            # Parse selected capsules from MiniZinc output
            selected_capsules = []
            
            # Look for capsule indices in the output
            import re
            indices_match = re.search(r'Capsule indices: \[([^\]]+)\]', results_content)
            if indices_match:
                indices_str = indices_match.group(1)
                selected_indices = [int(x.strip()) for x in indices_str.split(',') if x.strip()]
                # Convert from 1-based to 0-based indexing
                selected_indices = [i - 1 for i in selected_indices if 1 <= i <= len(capsules)]
                selected_capsules = [capsules[i] for i in selected_indices]
                print(f"  Selected {len(selected_capsules)} capsules from optimization results")
            else:
                # Fallback: look for individual capsule lines
                capsule_lines = [line for line in results_content.split('\n') if line.startswith('Capsule')]
                if capsule_lines:
                    # Extract capsule numbers from lines like "Capsule 1: ..."
                    selected_indices = []
                    for line in capsule_lines:
                        match = re.search(r'Capsule (\d+):', line)
                        if match:
                            capsule_num = int(match.group(1))
                            if 1 <= capsule_num <= len(capsules):
                                selected_indices.append(capsule_num - 1)  # Convert to 0-based
                    selected_capsules = [capsules[i] for i in selected_indices]
                    print(f"  Selected {len(selected_capsules)} capsules from line parsing")
                else:
                    # Final fallback: use all capsules
                    selected_capsules = capsules
                    print("  Using all capsules as fallback (no selection found in results)")
            
            print(f"  Processing {len(selected_capsules)} selected capsules")
            
            # Generate GLTF (reusing existing code)
            from minizinc_to_gltf import GLTFCapsuleGenerator
            
            generator = GLTFCapsuleGenerator()
            
            # Convert capsules to the format expected by the generator
            capsule_data_list = []
            for capsule in selected_capsules:
                capsule_data = {
                    'position': tuple(capsule['center']),
                    'length': capsule['height'],
                    'radius1': capsule['radius_top'],
                    'radius2': capsule['radius_bottom'],
                    'bone_name': capsule.get('bone_name', f"Capsule_{capsule['id']}"),
                    'rotation_matrix': None  # Could be derived from swing/twist rotations
                }
                capsule_data_list.append(capsule_data)
            
            # Generate GLTF with flat structure
            gltf_data = generator.generate_gltf(capsule_data_list, None)
            generator.save_gltf(output_gltf_path)
            
            print(f"  Generated GLTF file: {output_gltf_path}")
            return True
        except Exception as e:
            print(f"  Error processing results: {e}")
            return False
    
    def run_complete_pipeline(self, 
                             coacd_threshold: float = 0.05,
                             witness_points: int = 5000,
                             max_capsules: int = 50) -> bool:
        """Run the complete pipeline."""
        print(f"Starting CoACD-based Tapered Capsule Optimization Pipeline")
        print(f"Input VRM: {self.vrm_path}")
        print(f"Output directory: {self.output_dir}")
        print("-" * 60)
        
        # Step 1: Load mesh
        if not self.load_mesh_data():
            print("Pipeline failed at mesh loading step")
            return False
        
        # Create a mock mesh object for compatibility with existing methods
        class MockMesh:
            def __init__(self, vertices, bounds):
                self.vertices = vertices
                self.bounds = bounds
                
            def sample(self, num_points, return_index=False):
                # Sample points within bounds
                points = np.random.uniform(self.bounds[0], self.bounds[1], (num_points, 3))
                if return_index:
                    return points, np.arange(num_points)
                return points
        
        # Create mock mesh with vertices from mesh_data_extractor
        vertices = np.array(self.mesh_data_extractor.get_vertices())
        if len(vertices) > 0:
            bounds = np.array([np.min(vertices, axis=0), np.max(vertices, axis=0)])
        else:
            bounds = np.array([[-1, -1, -1], [1, 1, 1]])
        
        mesh = MockMesh(vertices, bounds)
        
        print("-" * 60)
        
        # Step 2: Run CoACD decomposition
        hulls = self.run_coacd_decomposition(mesh, coacd_threshold)
        if not hulls:
            print("Pipeline failed at CoACD decomposition step")
            return False
        
        print("-" * 60)
        
        # Step 3: Generate candidate capsules
        capsules = self.generate_candidate_capsules(hulls)
        if not capsules:
            print("Pipeline failed at capsule generation step")
            return False
        
        print("-" * 60)
        
        # Step 4: Sample witness points
        witness_points = self.sample_witness_points(mesh, witness_points)
        if witness_points is None:
            print("Pipeline failed at witness point sampling step")
            return False
        
        print("-" * 60)
        
        # Step 5: Build coverage matrix
        coverage_matrix = self.build_coverage_matrix(capsules, witness_points)
        if coverage_matrix is None:
            print("Pipeline failed at coverage matrix construction step")
            return False
        
        print("-" * 60)
        
        # Step 6: Create MiniZinc data file
        data_file = self.output_dir / f"{self.vrm_path.stem}_coacd_data.dzn"
        if not self.create_minizinc_data_file(capsules, witness_points, coverage_matrix, str(data_file)):
            print("Pipeline failed at MiniZinc data file creation step")
            return False
        
        print("-" * 60)
        
        # Step 7: Run MiniZinc optimization (if model exists)
        model_file = Path(__file__).parent / "coacd_capsule_model.mzn"
        results_file = self.output_dir / f"{self.vrm_path.stem}_coacd_results.txt"
        
        if model_file.exists():
            print("Step 7: Running MiniZinc optimization")
            if self.run_minizinc_optimization(str(model_file), str(data_file), str(results_file)):
                print("  MiniZinc optimization completed successfully")
            else:
                print("  MiniZinc optimization failed, using all capsules as fallback")
        else:
            print("Step 7: MiniZinc model not found, using all capsules as selected set")
            # Create a simple results file with all capsules selected
            with open(results_file, 'w') as f:
                f.write(f"Selected capsules: {len(capsules)}\n")
                f.write("Capsule indices: [" + ", ".join(str(i+1) for i in range(len(capsules))) + "]\n")
                for i, capsule in enumerate(capsules):
                    f.write(f"Capsule {i+1}: center({capsule['center'][0]}, {capsule['center'][1]}, {capsule['center'][2]}) "
                            f"height({capsule['height']}) radii({capsule['radius_top']}, {capsule['radius_bottom']}) "
                            f"swing({capsule['swing_rotation'][0]}, {capsule['swing_rotation'][1]}, {capsule['swing_rotation'][2]}) "
                            f"twist({capsule['twist_rotation']})\n")
        
        print("-" * 60)
        
        # Step 8: Process results
        gltf_file = self.output_dir / f"{self.vrm_path.stem}_coacd_capsules.gltf"
        if not self.process_results(capsules, str(results_file), str(gltf_file)):
            print("Pipeline failed at results processing step")
            return False
        
        print("-" * 60)
        print("Pipeline completed successfully!")
        print(f"Output files:")
        print(f"  Data file: {data_file}")
        print(f"  GLTF file: {gltf_file}")
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CoACD-based Tapered Capsule Optimization Pipeline"
    )
    parser.add_argument("vrm_file", help="Input VRM file")
    parser.add_argument("-o", "--output-dir", help="Output directory (default: same as input)")
    parser.add_argument("--threshold", type=float, default=0.05, 
                       help="CoACD decomposition threshold (default: 0.05)")
    parser.add_argument("--points", type=int, default=5000,
                       help="Number of witness points (default: 5000)")
    parser.add_argument("--max-capsules", type=int, default=50,
                       help="Maximum number of capsules (default: 50)")
    
    args = parser.parse_args()
    
    # Validate input file
    vrm_path = Path(args.vrm_file)
    if not vrm_path.exists():
        print(f"Error: VRM file not found: {vrm_path}")
        sys.exit(1)
    
    try:
        # Create and run pipeline
        pipeline = CoACDCapsulePipeline(str(vrm_path), args.output_dir)
        
        success = pipeline.run_complete_pipeline(
            coacd_threshold=args.threshold,
            witness_points=args.points,
            max_capsules=args.max_capsules
        )
        
        if not success:
            print("\nPipeline failed. Check the error messages above.")
            sys.exit(1)
        
        print("\nPipeline completed successfully!")
        
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
