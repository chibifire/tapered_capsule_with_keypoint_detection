#!/usr/bin/env python3
"""
Convert MiniZinc tapered capsule optimization output to glTF format.
Can ingest existing VRM1 models and replace with optimized capsule geometry.
"""

import json
import math
import sys
import re
import base64
import struct
import numpy as np
from typing import List, Dict, Tuple, Any
from capsule_skinning import CapsuleSkinningSystem

class GLTFCapsuleGenerator:
    def __init__(self):
        self.gltf_data = {
            "asset": {
                "version": "2.0",
                "generator": "MiniZinc Capsule Optimizer",
                "copyright": "Generated from VRM optimization"
            },
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [],
            "meshes": [],
            "accessors": [],
            "bufferViews": [],
            "buffers": [],
            "materials": [
                {
                    "name": "CapsuleMaterial",
                    "pbrMetallicRoughness": {
                        "baseColorFactor": [0.8, 0.2, 0.2, 1.0],
                        "metallicFactor": 0.0,
                        "roughnessFactor": 0.8
                    }
                }
            ]
        }
        self.buffer_data = bytearray()
        self.accessor_offset = 0
        self.buffer_view_offset = 0
        self.buffer_offset = 0
        self.node_offset = 0
        
    def generate_capsule_mesh(self, length: float, radius1: float, radius2: float, 
                            rotation_matrix: List[List[float]] = None,
                            segments: int = 16) -> Dict[str, Any]:
        """Generate mesh data for a tapered capsule centered at origin with NO rotation applied (pure geometry)."""
        vertices = []
        normals = []
        indices = []
        
        # Generate tapered cylinder body with multiple rings for smooth tapering
        cylinder_rings = 8  # Number of rings along the cylinder for smooth tapering
        
        for ring in range(cylinder_rings + 1):
            # Interpolate position and radius along the cylinder
            t = ring / cylinder_rings  # 0 to 1 from bottom to top
            y_pos = -length / 2 + t * length  # Centered at origin
            
            # Linear interpolation between bottom and top radius
            current_radius = radius1 + t * (radius2 - radius1)
            
            for i in range(segments):
                theta = i * 2 * math.pi / segments
                cos_theta = math.cos(theta)
                sin_theta = math.sin(theta)
                
                x = current_radius * cos_theta  # No position offset
                y = y_pos
                z = current_radius * sin_theta  # No position offset
                vertices.extend([x, y, z])
                
                # Calculate normal for tapered surface
                # For tapered cylinder, normal needs to account for the slope
                radius_diff = radius2 - radius1
                slope_factor = radius_diff / length if length > 0 else 0
                
                # Normal vector accounting for taper
                nx = cos_theta
                ny = slope_factor  # Y component based on taper
                nz = sin_theta
                
                # Normalize the normal vector
                normal_length = math.sqrt(nx*nx + ny*ny + nz*nz)
                if normal_length > 0:
                    nx /= normal_length
                    ny /= normal_length
                    nz /= normal_length
                
                normals.extend([nx, ny, nz])
        
        # Generate bottom hemisphere (using radius1)
        hemisphere_segments = segments // 2
        
        # Add bottom cap center vertex
        vertices.extend([0, -length / 2, 0])
        normals.extend([0, -1, 0])
        bottom_center_idx = len(vertices) // 3 - 1
        
        for j in range(1, hemisphere_segments + 1):
            phi = -math.pi / 2 + j * (math.pi / 2) / hemisphere_segments
            y_offset = radius1 * math.sin(phi)
            radius_at_phi = radius1 * math.cos(phi)
            
            for i in range(segments):
                theta = i * 2 * math.pi / segments
                x = radius_at_phi * math.cos(theta)  # No position offset
                y = -length / 2 + y_offset  # Centered at origin
                z = radius_at_phi * math.sin(theta)  # No position offset
                vertices.extend([x, y, z])
                
                # Normal for hemisphere
                nx = math.cos(phi) * math.cos(theta)
                ny = math.sin(phi)
                nz = math.cos(phi) * math.sin(theta)
                normals.extend([nx, ny, nz])
        
        # Generate top hemisphere (using radius2)
        for j in range(1, hemisphere_segments + 1):
            phi = j * (math.pi / 2) / hemisphere_segments
            y_offset = radius2 * math.sin(phi)
            radius_at_phi = radius2 * math.cos(phi)
            
            for i in range(segments):
                theta = i * 2 * math.pi / segments
                x = radius_at_phi * math.cos(theta)  # No position offset
                y = length / 2 + y_offset  # Centered at origin
                z = radius_at_phi * math.sin(theta)  # No position offset
                vertices.extend([x, y, z])
                
                # Normal for hemisphere
                nx = math.cos(phi) * math.cos(theta)
                ny = math.sin(phi)
                nz = math.cos(phi) * math.sin(theta)
                normals.extend([nx, ny, nz])
        
        # Add top cap center vertex
        vertices.extend([0, length / 2, 0])
        normals.extend([0, 1, 0])
        top_center_idx = len(vertices) // 3 - 1
        
        # Generate indices for tapered cylinder body
        for ring in range(cylinder_rings):
            for i in range(segments):
                next_i = (i + 1) % segments
                
                # Current ring indices
                curr_ring_start = ring * segments
                next_ring_start = (ring + 1) * segments
                
                curr_i = curr_ring_start + i
                curr_next = curr_ring_start + next_i
                next_i_idx = next_ring_start + i
                next_next = next_ring_start + next_i
                
                # Two triangles per quad (fixed winding order for outward-facing normals)
                indices.extend([curr_i, next_i_idx, curr_next])
                indices.extend([curr_next, next_i_idx, next_next])
        
        # Generate indices for hemispheres
        base_cylinder = (cylinder_rings + 1) * segments
        bottom_center_idx = base_cylinder  # Index of bottom center vertex
        bottom_hemisphere_start = bottom_center_idx + 1
        
        # Connect bottom center to first ring of bottom hemisphere
        for i in range(segments):
            next_i = (i + 1) % segments
            indices.extend([bottom_center_idx, bottom_hemisphere_start + next_i, bottom_hemisphere_start + i])
        
        # Connect bottom hemisphere to cylinder bottom
        cylinder_bottom_ring = 0  # First ring of cylinder
        bottom_hemisphere_last_ring = bottom_hemisphere_start + (hemisphere_segments - 1) * segments
        for i in range(segments):
            next_i = (i + 1) % segments
            indices.extend([
                cylinder_bottom_ring + i, bottom_hemisphere_last_ring + i, cylinder_bottom_ring + next_i
            ])
            indices.extend([
                cylinder_bottom_ring + next_i, bottom_hemisphere_last_ring + i, bottom_hemisphere_last_ring + next_i
            ])
        
        # Bottom hemisphere internal rings
        for j in range(hemisphere_segments - 1):
            for i in range(segments):
                next_i = (i + 1) % segments
                
                curr_ring = bottom_hemisphere_start + j * segments
                next_ring = bottom_hemisphere_start + (j + 1) * segments
                
                indices.extend([
                    curr_ring + i, next_ring + i, curr_ring + next_i
                ])
                indices.extend([
                    curr_ring + next_i, next_ring + i, next_ring + next_i
                ])
        
        # Top hemisphere indices
        top_hemisphere_start = bottom_hemisphere_start + hemisphere_segments * segments
        top_center_idx = top_hemisphere_start + hemisphere_segments * segments
        
        # Connect cylinder top to top hemisphere
        cylinder_top_ring = cylinder_rings * segments  # Last ring of cylinder
        top_hemisphere_first_ring = top_hemisphere_start
        for i in range(segments):
            next_i = (i + 1) % segments
            indices.extend([
                cylinder_top_ring + i, top_hemisphere_first_ring + next_i, top_hemisphere_first_ring + i
            ])
            indices.extend([
                cylinder_top_ring + i, cylinder_top_ring + next_i, top_hemisphere_first_ring + next_i
            ])
        
        # Top hemisphere internal rings
        for j in range(hemisphere_segments - 1):
            for i in range(segments):
                next_i = (i + 1) % segments
                
                curr_ring = top_hemisphere_start + j * segments
                next_ring = top_hemisphere_start + (j + 1) * segments
                
                indices.extend([
                    curr_ring + i, next_ring + i, curr_ring + next_i
                ])
                indices.extend([
                    curr_ring + next_i, next_ring + i, next_ring + next_i
                ])
        
        # Connect top hemisphere last ring to top center
        top_hemisphere_last_ring = top_hemisphere_start + (hemisphere_segments - 1) * segments
        for i in range(segments):
            next_i = (i + 1) % segments
            indices.extend([top_hemisphere_last_ring + i, top_center_idx, top_hemisphere_last_ring + next_i])
        
        # Note: Rotation is now handled at the node level, not during mesh generation
        # This allows for proper local transformations in the glTF structure
        
        return {
            'vertices': vertices,
            'normals': normals,
            'indices': indices
        }
    
    def add_buffer_data(self, data: List[float], component_type: int = 5126) -> int:
        """Add data to buffer and return accessor index."""
        # Convert to bytes
        if component_type == 5126:  # FLOAT
            byte_data = struct.pack(f'{len(data)}f', *data)
        elif component_type == 5123:  # UNSIGNED_SHORT
            byte_data = struct.pack(f'{len(data)}H', *data)
        elif component_type == 5125:  # UNSIGNED_INT
            byte_data = struct.pack(f'{len(data)}I', *data)
        else:
            raise ValueError(f"Unsupported component type: {component_type}")
        
        # Align to 4-byte boundary
        while len(self.buffer_data) % 4 != 0:
            self.buffer_data.append(0)
        
        byte_offset = len(self.buffer_data)
        self.buffer_data.extend(byte_data)
        
        # Create buffer view
        buffer_view_index = len(self.gltf_data["bufferViews"])
        self.gltf_data["bufferViews"].append({
            "buffer": 0,
            "byteOffset": byte_offset,
            "byteLength": len(byte_data)
        })
        
        return buffer_view_index
    
    def create_accessor(self, buffer_view: int, count: int, type_str: str, 
                       component_type: int, min_vals: List[float] = None, 
                       max_vals: List[float] = None) -> int:
        """Create accessor for buffer data."""
        accessor_index = len(self.gltf_data["accessors"])
        accessor = {
            "bufferView": buffer_view,
            "byteOffset": 0,
            "componentType": component_type,
            "count": count,
            "type": type_str
        }
        
        if min_vals:
            accessor["min"] = min_vals
        if max_vals:
            accessor["max"] = max_vals
            
        self.gltf_data["accessors"].append(accessor)
        return accessor_index
    
    def add_capsule_to_scene(self, capsule_data: Dict[str, Any], capsule_id: int, 
                           position: Tuple[float, float, float] = (0, 0, 0),
                           rotation_matrix: List[List[float]] = None,
                           bone_name: str = None,
                           skinning_data: Dict[str, Any] = None,
                           vertex_colors: np.ndarray = None):
        """Add a capsule mesh to the glTF scene with local node transformation and optional skinning."""
        vertices = capsule_data['vertices']
        normals = capsule_data['normals']
        indices = capsule_data['indices']
        
        # Calculate bounding box
        vertex_count = len(vertices) // 3
        min_pos = [min(vertices[i::3]) for i in range(3)]
        max_pos = [max(vertices[i::3]) for i in range(3)]
        
        # Add vertex data to buffer
        vertex_buffer_view = self.add_buffer_data(vertices, 5126)  # FLOAT
        vertex_accessor = self.create_accessor(
            vertex_buffer_view, vertex_count, "VEC3", 5126, min_pos, max_pos
        )
        
        # Add normal data to buffer
        normal_buffer_view = self.add_buffer_data(normals, 5126)  # FLOAT
        normal_accessor = self.create_accessor(
            normal_buffer_view, vertex_count, "VEC3", 5126
        )
        
        # Add index data to buffer
        index_buffer_view = self.add_buffer_data(indices, 5125)  # UNSIGNED_INT
        index_accessor = self.create_accessor(
            index_buffer_view, len(indices), "SCALAR", 5125
        )
        
        # Prepare mesh attributes
        attributes = {
            "POSITION": vertex_accessor,
            "NORMAL": normal_accessor
        }
        
        # Add skinning data if provided
        if skinning_data:
            if "joints" in skinning_data and "weights" in skinning_data:
                joints_data = skinning_data["joints"]
                weights_data = skinning_data["weights"]
                
                # Add JOINTS_0 attribute (bone indices)
                joints_flat = joints_data.flatten().astype(np.uint16)
                joints_buffer_view = self.add_buffer_data(joints_flat.tolist(), 5123)  # UNSIGNED_SHORT
                joints_accessor = self.create_accessor(
                    joints_buffer_view, len(joints_data), "VEC4", 5123
                )
                attributes["JOINTS_0"] = joints_accessor
                
                # Add WEIGHTS_0 attribute (bone weights)
                weights_flat = weights_data.flatten().astype(np.float32)
                weights_buffer_view = self.add_buffer_data(weights_flat.tolist(), 5126)  # FLOAT
                weights_accessor = self.create_accessor(
                    weights_buffer_view, len(weights_data), "VEC4", 5126
                )
                attributes["WEIGHTS_0"] = weights_accessor
                
                print(f"Added skinning data to capsule {capsule_id}: {len(joints_data)} vertices with bone influences")
        
        # Add vertex colors if provided
        if vertex_colors is not None:
            colors_flat = vertex_colors.flatten().astype(np.float32)
            colors_buffer_view = self.add_buffer_data(colors_flat.tolist(), 5126)  # FLOAT
            colors_accessor = self.create_accessor(
                colors_buffer_view, len(vertex_colors), "VEC3", 5126
            )
            attributes["COLOR_0"] = colors_accessor
            print(f"Added vertex colors to capsule {capsule_id}: {len(vertex_colors)} vertices")
        
        # Create mesh
        mesh_index = len(self.gltf_data["meshes"])
        self.gltf_data["meshes"].append({
            "name": f"Capsule_{capsule_id}",
            "primitives": [{
                "attributes": attributes,
                "indices": index_accessor,
                "material": 0
            }]
        })
        
        # Create node with local transformation
        node_index = len(self.gltf_data["nodes"])
        if bone_name:
            # Clean up bone name - remove problematic characters and ensure proper formatting
            clean_bone_name = bone_name.replace("(", "_").replace(")", "_").replace("$", "_").replace(" ", "_")
            # Remove multiple underscores and trailing underscores
            clean_bone_name = "_".join(filter(None, clean_bone_name.split("_")))
            node_name = f"Capsule_{clean_bone_name}_{capsule_id}"
        else:
            node_name = f"CapsuleNode_{capsule_id}"
        
        node = {
            "name": node_name,
            "mesh": mesh_index
        }
        
        # Add translation (position) to node
        if position != (0, 0, 0):
            node["translation"] = list(position)
        
        # Add rotation to node (convert 3x3 matrix to quaternion)
        if rotation_matrix:
            # Check if rotation matrix is not identity
            is_identity = (
                abs(rotation_matrix[0][0] - 1.0) < 0.001 and abs(rotation_matrix[0][1]) < 0.001 and abs(rotation_matrix[0][2]) < 0.001 and
                abs(rotation_matrix[1][0]) < 0.001 and abs(rotation_matrix[1][1] - 1.0) < 0.001 and abs(rotation_matrix[1][2]) < 0.001 and
                abs(rotation_matrix[2][0]) < 0.001 and abs(rotation_matrix[2][1]) < 0.001 and abs(rotation_matrix[2][2] - 1.0) < 0.001
            )
            
            if not is_identity:
                quaternion = self.matrix_to_quaternion(rotation_matrix)
                node["rotation"] = quaternion
                print(f"Applied rotation to {node_name}: matrix={rotation_matrix}, quaternion={quaternion}")
            else:
                print(f"Skipped identity rotation for {node_name}")
        
        self.gltf_data["nodes"].append(node)
        
        return node_index
    
    def load_vrm_model(self, vrm_path: str) -> Dict[str, Any]:
        """Load existing VRM model to extract skeleton information."""
        try:
            with open(vrm_path, 'rb') as f:
                # Check if it's binary glTF (.glb) or JSON (.gltf)
                magic = f.read(4)
                f.seek(0)
                
                if magic == b'glTF':
                    # Binary glTF format
                    return self.load_glb(f)
                else:
                    # JSON glTF format
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load VRM model {vrm_path}: {e}")
            return {}
    
    def load_glb(self, file) -> Dict[str, Any]:
        """Load binary glTF (.glb) file."""
        # Read header
        magic = struct.unpack('4s', file.read(4))[0]
        version = struct.unpack('I', file.read(4))[0]
        length = struct.unpack('I', file.read(4))[0]
        
        # Read JSON chunk
        json_chunk_length = struct.unpack('I', file.read(4))[0]
        json_chunk_type = struct.unpack('4s', file.read(4))[0]
        json_data = json.loads(file.read(json_chunk_length).decode('utf-8'))
        
        return json_data
    
    def parse_dzn_file(self, dzn_path: str) -> Dict[str, Any]:
        """Parse DZN file to extract bone rotation matrices, directions, and other data."""
        bone_data = {}
        
        try:
            with open(dzn_path, 'r') as f:
                content = f.read()
            
            # Extract bone names
            bone_names_match = re.search(r'bone_names = \[(.*?)\];', content, re.DOTALL)
            if bone_names_match:
                names_str = bone_names_match.group(1)
                bone_names = [name.strip().strip('"') for name in names_str.split(',')]
                bone_data['bone_names'] = bone_names
            
            # Extract bone rotations (3x3 matrices flattened to 9 elements, scaled by 1000)
            rotations_match = re.search(r'bone_rotations = array2d\(1\.\.\d+, 1\.\.9, \[(.*?)\]\);', content, re.DOTALL)
            if rotations_match:
                rotations_str = rotations_match.group(1)
                rotation_values = [int(x.strip()) for x in rotations_str.split(',')]
                
                # Group into 3x3 matrices (9 elements each)
                bone_rotations = {}
                for i, bone_name in enumerate(bone_names):
                    start_idx = i * 9
                    if start_idx + 8 < len(rotation_values):
                        # Extract 9 values and convert back from scaled integers
                        matrix_values = [rotation_values[start_idx + j] / 1000.0 for j in range(9)]
                        # Reshape to 3x3 matrix
                        rotation_matrix = [
                            [matrix_values[0], matrix_values[1], matrix_values[2]],
                            [matrix_values[3], matrix_values[4], matrix_values[5]],
                            [matrix_values[6], matrix_values[7], matrix_values[8]]
                        ]
                        bone_rotations[bone_name] = rotation_matrix
                
                bone_data['bone_rotations'] = bone_rotations
            
            # Extract bone directions (3D vectors, scaled by 1000)
            directions_match = re.search(r'bone_directions = array2d\(1\.\.\d+, 1\.\.3, \[(.*?)\]\);', content, re.DOTALL)
            if directions_match:
                directions_str = directions_match.group(1)
                direction_values = [int(x.strip()) for x in directions_str.split(',')]
                
                # Group into 3D vectors (3 elements each)
                bone_directions = {}
                for i, bone_name in enumerate(bone_names):
                    start_idx = i * 3
                    if start_idx + 2 < len(direction_values):
                        # Extract 3 values and convert back from scaled integers
                        direction_vector = [
                            direction_values[start_idx] / 1000.0,
                            direction_values[start_idx + 1] / 1000.0,
                            direction_values[start_idx + 2] / 1000.0
                        ]
                        bone_directions[bone_name] = direction_vector
                
                bone_data['bone_directions'] = bone_directions
            
            return bone_data
            
        except Exception as e:
            print(f"Warning: Could not parse DZN file {dzn_path}: {e}")
            return {}
    
    def apply_rotation_to_vector(self, vector: List[float], rotation_matrix: List[List[float]]) -> List[float]:
        """Apply 3x3 rotation matrix to a 3D vector."""
        x, y, z = vector
        result = [
            rotation_matrix[0][0] * x + rotation_matrix[0][1] * y + rotation_matrix[0][2] * z,
            rotation_matrix[1][0] * x + rotation_matrix[1][1] * y + rotation_matrix[1][2] * z,
            rotation_matrix[2][0] * x + rotation_matrix[2][1] * y + rotation_matrix[2][2] * z
        ]
        return result
    
    def calculate_swing_rotation(self, from_vector: List[float], to_vector: List[float]) -> List[List[float]]:
        """Calculate rotation matrix to align from_vector with to_vector (swing rotation)."""
        import math
        
        # Normalize input vectors
        from_len = math.sqrt(sum(x*x for x in from_vector))
        to_len = math.sqrt(sum(x*x for x in to_vector))
        
        if from_len < 0.001 or to_len < 0.001:
            return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Identity matrix
        
        from_vec = [x / from_len for x in from_vector]
        to_vec = [x / to_len for x in to_vector]
        
        # Check if vectors are already aligned
        dot_product = sum(from_vec[i] * to_vec[i] for i in range(3))
        
        if dot_product > 0.9999:  # Already aligned
            return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        elif dot_product < -0.9999:  # Opposite directions
            # Find a perpendicular vector for 180-degree rotation
            if abs(from_vec[0]) < 0.9:
                perp = [1, 0, 0]
            else:
                perp = [0, 1, 0]
            
            # Create perpendicular vector using cross product
            axis = [
                from_vec[1] * perp[2] - from_vec[2] * perp[1],
                from_vec[2] * perp[0] - from_vec[0] * perp[2],
                from_vec[0] * perp[1] - from_vec[1] * perp[0]
            ]
            axis_len = math.sqrt(sum(x*x for x in axis))
            if axis_len > 0.001:
                axis = [x / axis_len for x in axis]
                # 180-degree rotation around perpendicular axis
                return self.axis_angle_to_matrix(axis, math.pi)
        
        # Calculate rotation axis (cross product)
        axis = [
            from_vec[1] * to_vec[2] - from_vec[2] * to_vec[1],
            from_vec[2] * to_vec[0] - from_vec[0] * to_vec[2],
            from_vec[0] * to_vec[1] - from_vec[1] * to_vec[0]
        ]
        axis_len = math.sqrt(sum(x*x for x in axis))
        
        if axis_len < 0.001:  # Vectors are parallel
            return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        
        axis = [x / axis_len for x in axis]
        
        # Calculate rotation angle
        angle = math.acos(max(-1.0, min(1.0, dot_product)))
        
        # Convert axis-angle to rotation matrix
        return self.axis_angle_to_matrix(axis, angle)
    
    def axis_angle_to_matrix(self, axis: List[float], angle: float) -> List[List[float]]:
        """Convert axis-angle representation to 3x3 rotation matrix."""
        import math
        
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        one_minus_cos = 1 - cos_angle
        
        x, y, z = axis
        
        return [
            [cos_angle + x*x*one_minus_cos, x*y*one_minus_cos - z*sin_angle, x*z*one_minus_cos + y*sin_angle],
            [y*x*one_minus_cos + z*sin_angle, cos_angle + y*y*one_minus_cos, y*z*one_minus_cos - x*sin_angle],
            [z*x*one_minus_cos - y*sin_angle, z*y*one_minus_cos + x*sin_angle, cos_angle + z*z*one_minus_cos]
        ]
    
    def multiply_matrices(self, a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        """Multiply two 3x3 matrices."""
        result = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    result[i][j] += a[i][k] * b[k][j]
        return result
    
    def matrix_to_quaternion(self, matrix: List[List[float]]) -> List[float]:
        """Convert 3x3 rotation matrix to quaternion [x, y, z, w]."""
        import math
        
        # Extract matrix elements
        m00, m01, m02 = matrix[0]
        m10, m11, m12 = matrix[1]
        m20, m21, m22 = matrix[2]
        
        # Calculate trace
        trace = m00 + m11 + m22
        
        if trace > 0:
            s = math.sqrt(trace + 1.0) * 2  # s = 4 * qw
            w = 0.25 * s
            x = (m21 - m12) / s
            y = (m02 - m20) / s
            z = (m10 - m01) / s
        elif m00 > m11 and m00 > m22:
            s = math.sqrt(1.0 + m00 - m11 - m22) * 2  # s = 4 * qx
            w = (m21 - m12) / s
            x = 0.25 * s
            y = (m01 + m10) / s
            z = (m02 + m20) / s
        elif m11 > m22:
            s = math.sqrt(1.0 + m11 - m00 - m22) * 2  # s = 4 * qy
            w = (m02 - m20) / s
            x = (m01 + m10) / s
            y = 0.25 * s
            z = (m12 + m21) / s
        else:
            s = math.sqrt(1.0 + m22 - m00 - m11) * 2  # s = 4 * qz
            w = (m10 - m01) / s
            x = (m02 + m20) / s
            y = (m12 + m21) / s
            z = 0.25 * s
        
        return [x, y, z, w]
    
    def parse_minizinc_output(self, output_text: str, manual_scale: float = None, dzn_path: str = None) -> List[Dict[str, Any]]:
        """Parse MiniZinc solver output to extract capsule parameters."""
        capsules = []
        
        # Parse bone rotation and direction data from DZN file if provided
        bone_data = {}
        if dzn_path:
            bone_data = self.parse_dzn_file(dzn_path)
            if bone_data.get('bone_rotations'):
                print(f"Loaded bone rotations for {len(bone_data['bone_rotations'])} bones")
            if bone_data.get('bone_directions'):
                print(f"Loaded bone directions for {len(bone_data['bone_directions'])} bones")
        
        # Determine scale factor
        if manual_scale is not None:
            scale_factor = manual_scale
            print(f"Using manual scale factor: {scale_factor}")
        else:
            # Auto-detect scaling from output
            is_scaled = "Integer scaling: 1000x" in output_text
            scale_factor = 1000.0 if is_scaled else 1.0
            if is_scaled:
                print(f"Auto-detected scale factor: {scale_factor}")
        
        lines = output_text.strip().split('\n')
        for line in lines:
            if line.startswith('Capsule'):
                # Parse new format: Capsule 1: pos(-84,792,-5) len(422) radii(164,164) bone(...) rot_swing(...) dir(...)
                # First try the new format with rotation swing
                match = re.search(
                    r'Capsule \d+: pos\(([-\d.]+),([-\d.]+),([-\d.]+)\) len\(([-\d.]+)\) radii\(([-\d.]+),([-\d.]+)\) bone\(([^)]+)\) rot_swing\(([-\d.,]+)\) dir\(([-\d.,-]+)\)', 
                    line
                )
                if match:
                    pos_x, pos_y, pos_z, length, r1, r2, bone_name, rot_swing_str, dir_str = match.groups()
                    pos_x, pos_y, pos_z, length, r1, r2 = map(float, [pos_x, pos_y, pos_z, length, r1, r2])
                    
                    # Parse rotation swing matrix (9 values, scaled by 1000)
                    rot_swing_values = [float(x.strip()) for x in rot_swing_str.split(',')]
                    if len(rot_swing_values) == 9:
                        # Convert back from scaled integers and reshape to 3x3 matrix
                        rotation_matrix = [
                            [rot_swing_values[0] / 1000.0, rot_swing_values[1] / 1000.0, rot_swing_values[2] / 1000.0],
                            [rot_swing_values[3] / 1000.0, rot_swing_values[4] / 1000.0, rot_swing_values[5] / 1000.0],
                            [rot_swing_values[6] / 1000.0, rot_swing_values[7] / 1000.0, rot_swing_values[8] / 1000.0]
                        ]
                        
                        # Check if rotation matrix is identity (all identity matrices indicate no rotation data)
                        is_identity = (
                            abs(rotation_matrix[0][0] - 1.0) < 0.001 and abs(rotation_matrix[0][1]) < 0.001 and abs(rotation_matrix[0][2]) < 0.001 and
                            abs(rotation_matrix[1][0]) < 0.001 and abs(rotation_matrix[1][1] - 1.0) < 0.001 and abs(rotation_matrix[1][2]) < 0.001 and
                            abs(rotation_matrix[2][0]) < 0.001 and abs(rotation_matrix[2][1]) < 0.001 and abs(rotation_matrix[2][2] - 1.0) < 0.001
                        )
                        
                        if is_identity:
                            rotation_matrix = None  # Treat identity as no rotation
                    else:
                        rotation_matrix = None
                    
                    # Parse bone direction (3 values, scaled by 1000)
                    dir_values = [float(x.strip()) for x in dir_str.split(',')]
                    if len(dir_values) == 3:
                        bone_direction = [dir_values[0] / 1000.0, dir_values[1] / 1000.0, dir_values[2] / 1000.0]
                        
                        # If we have a bone direction but no rotation matrix, calculate rotation from direction
                        if bone_direction and any(abs(x) > 0.001 for x in bone_direction) and rotation_matrix is None:
                            default_capsule_direction = [0, 1, 0]  # Capsule points along Y-axis by default
                            rotation_matrix = self.calculate_swing_rotation(default_capsule_direction, bone_direction)
                            print(f"Calculated rotation from bone direction {bone_direction} for {bone_name}")
                    else:
                        bone_direction = None
                    
                    # Scale back to real-world coordinates if scale factor > 1
                    if scale_factor > 1.0:
                        pos_x /= scale_factor
                        pos_y /= scale_factor
                        pos_z /= scale_factor
                        length /= scale_factor
                        r1 /= scale_factor
                        r2 /= scale_factor
                    
                    capsules.append({
                        'position': (pos_x, pos_y, pos_z),
                        'length': length,
                        'radius1': r1,
                        'radius2': r2,
                        'bone_name': bone_name,
                        'rotation_matrix': rotation_matrix,
                        'bone_direction': bone_direction
                    })
                else:
                    # Fallback to old format: Capsule 1: pos(-84,792,-5) len(422) radii(164,164) bone(...)
                    match = re.search(
                        r'Capsule \d+: pos\(([-\d.]+),([-\d.]+),([-\d.]+)\) len\(([-\d.]+)\) radii\(([-\d.]+),([-\d.]+)\) bone\(([^)]+)\)', 
                        line
                    )
                    if match:
                        pos_x, pos_y, pos_z, length, r1, r2, bone_name = match.groups()
                        pos_x, pos_y, pos_z, length, r1, r2 = map(float, [pos_x, pos_y, pos_z, length, r1, r2])
                        
                        # Scale back to real-world coordinates if scale factor > 1
                        if scale_factor > 1.0:
                            pos_x /= scale_factor
                            pos_y /= scale_factor
                            pos_z /= scale_factor
                            length /= scale_factor
                            r1 /= scale_factor
                            r2 /= scale_factor
                        
                        # Get bone rotation matrix and direction if available from DZN file
                        rotation_matrix = None
                        bone_direction = None
                        
                        if bone_data.get('bone_rotations') and bone_name in bone_data['bone_rotations']:
                            rotation_matrix = bone_data['bone_rotations'][bone_name]
                        
                        if bone_data.get('bone_directions') and bone_name in bone_data['bone_directions']:
                            bone_direction = bone_data['bone_directions'][bone_name]
                            
                            # Calculate swing rotation to align capsule Y-axis with bone direction
                            if bone_direction and any(abs(x) > 0.001 for x in bone_direction):
                                default_capsule_direction = [0, 1, 0]  # Capsule points along Y-axis by default
                                swing_rotation = self.calculate_swing_rotation(default_capsule_direction, bone_direction)
                                
                                # Combine with existing bone rotation if available
                                if rotation_matrix:
                                    rotation_matrix = self.multiply_matrices(swing_rotation, rotation_matrix)
                                else:
                                    rotation_matrix = swing_rotation
                        
                        capsules.append({
                            'position': (pos_x, pos_y, pos_z),
                            'length': length,
                            'radius1': r1,
                            'radius2': r2,
                            'bone_name': bone_name,
                            'rotation_matrix': rotation_matrix,
                            'bone_direction': bone_direction
                        })
        
        return capsules
    
    def build_bone_hierarchy(self, capsules: List[Dict[str, Any]], dzn_path: str = None) -> Dict[str, Any]:
        """Build bone hierarchy information from DZN file."""
        hierarchy_data = {}
        
        if not dzn_path:
            return hierarchy_data
            
        try:
            with open(dzn_path, 'r') as f:
                content = f.read()
            
            # Extract bone names
            bone_names_match = re.search(r'bone_names = \[(.*?)\];', content, re.DOTALL)
            if bone_names_match:
                names_str = bone_names_match.group(1)
                bone_names = [name.strip().strip('"') for name in names_str.split(',')]
                hierarchy_data['bone_names'] = bone_names
            
            # Extract bone parents
            parents_match = re.search(r'bone_parents = \[(.*?)\];', content, re.DOTALL)
            if parents_match:
                parents_str = parents_match.group(1)
                bone_parents = [int(x.strip()) for x in parents_str.split(',')]
                hierarchy_data['bone_parents'] = bone_parents
            
            # Extract bone children counts
            children_counts_match = re.search(r'bone_children_counts = \[(.*?)\];', content, re.DOTALL)
            if children_counts_match:
                counts_str = children_counts_match.group(1)
                bone_children_counts = [int(x.strip()) for x in counts_str.split(',')]
                hierarchy_data['bone_children_counts'] = bone_children_counts
            
            # Extract bone children indices
            children_indices_match = re.search(r'bone_children_indices = \[(.*?)\];', content, re.DOTALL)
            if children_indices_match:
                indices_str = children_indices_match.group(1)
                if indices_str.strip():  # Check if not empty
                    bone_children_indices = [int(x.strip()) for x in indices_str.split(',')]
                    hierarchy_data['bone_children_indices'] = bone_children_indices
                else:
                    hierarchy_data['bone_children_indices'] = []
            
            return hierarchy_data
            
        except Exception as e:
            print(f"Warning: Could not parse hierarchy from DZN file {dzn_path}: {e}")
            return {}
    
    def remap_vrm_bones(self, vrm_data: Dict[str, Any], capsules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Remap VRM humanoid bone indices to match our capsule nodes."""
        if not vrm_data or "extensions" not in vrm_data:
            return {}
        
        extensions = vrm_data["extensions"].copy()
        if "VRMC_vrm" not in extensions:
            return extensions
        
        vrm_ext = extensions["VRMC_vrm"].copy()
        if "humanoid" not in vrm_ext or "humanBones" not in vrm_ext["humanoid"]:
            return extensions
        
        # Create mapping from bone names to capsule node indices
        bone_to_node = {}
        for i, capsule in enumerate(capsules):
            bone_name = capsule.get('bone_name', '')
            if bone_name:
                # Extract clean bone name (remove parentheses and extra info)
                clean_bone_name = bone_name.split('(')[0].strip()
                # Map to our capsule node index (offset by 1 for root node)
                bone_to_node[clean_bone_name] = i + 1
        
        print(f"Bone to node mapping: {bone_to_node}")
        
        # Standard VRM bone name mappings to our simplified names
        vrm_bone_mappings = {
            'hips': ['Hips', 'hips'],
            'spine': ['Spine', 'spine'],
            'chest': ['Chest', 'chest'],
            'neck': ['Neck', 'neck'],
            'head': ['Head', 'head'],
            'leftShoulder': ['LeftShoulder', 'leftShoulder', 'Left shoulder', 'Shoulder_L'],
            'leftUpperArm': ['LeftUpperArm', 'leftUpperArm', 'UpperArm_L'],
            'leftLowerArm': ['LeftLowerArm', 'leftLowerArm', 'LowerArm_L'],
            'leftHand': ['LeftHand', 'leftHand', 'Hand_L'],
            'rightShoulder': ['RightShoulder', 'rightShoulder', 'Right shoulder', 'Shoulder_R'],
            'rightUpperArm': ['RightUpperArm', 'rightUpperArm', 'UpperArm_R'],
            'rightLowerArm': ['RightLowerArm', 'rightLowerArm', 'LowerArm_R'],
            'rightHand': ['RightHand', 'rightHand', 'Hand_R'],
            'leftUpperLeg': ['LeftUpperLeg', 'leftUpperLeg', 'UpperLeg_L'],
            'leftLowerLeg': ['LeftLowerLeg', 'leftLowerLeg', 'LowerLeg_L'],
            'leftFoot': ['LeftFoot', 'leftFoot', 'Foot_L'],
            'leftToes': ['LeftToes', 'leftToes', 'Toes_L'],
            'rightUpperLeg': ['RightUpperLeg', 'rightUpperLeg', 'UpperLeg_R'],
            'rightLowerLeg': ['RightLowerLeg', 'rightLowerLeg', 'LowerLeg_R'],
            'rightFoot': ['RightFoot', 'rightFoot', 'Foot_R'],
            'rightToes': ['RightToes', 'rightToes', 'Toes_R']
        }
        
        # Remap humanoid bones
        original_bones = vrm_ext["humanoid"]["humanBones"].copy()
        remapped_bones = {}
        
        for vrm_bone_name, bone_info in original_bones.items():
            # Find matching capsule for this VRM bone
            found_mapping = False
            
            # Check if we have a direct mapping
            for possible_name in vrm_bone_mappings.get(vrm_bone_name, [vrm_bone_name]):
                if possible_name in bone_to_node:
                    remapped_bones[vrm_bone_name] = {
                        "node": bone_to_node[possible_name]
                    }
                    found_mapping = True
                    print(f"Mapped VRM bone '{vrm_bone_name}' to node {bone_to_node[possible_name]} (capsule: {possible_name})")
                    break
            
            if not found_mapping:
                print(f"No capsule found for VRM bone '{vrm_bone_name}', skipping")
        
        # Update the VRM extension with remapped bones
        vrm_ext["humanoid"]["humanBones"] = remapped_bones
        extensions["VRMC_vrm"] = vrm_ext
        
        print(f"Remapped {len(remapped_bones)} VRM bones out of {len(original_bones)} original bones")
        return extensions

    def validate_gltf_structure(self) -> bool:
        """Validate the GLTF structure for common errors that cause import failures."""
        errors = []
        
        # Check accessor bounds
        for i, accessor in enumerate(self.gltf_data.get("accessors", [])):
            if "bufferView" in accessor:
                buffer_view_idx = accessor["bufferView"]
                if buffer_view_idx >= len(self.gltf_data.get("bufferViews", [])):
                    errors.append(f"Accessor {i} references invalid bufferView {buffer_view_idx}")
                else:
                    buffer_view = self.gltf_data["bufferViews"][buffer_view_idx]
                    buffer_idx = buffer_view.get("buffer", 0)
                    if buffer_idx >= len(self.gltf_data.get("buffers", [])):
                        errors.append(f"BufferView {buffer_view_idx} references invalid buffer {buffer_idx}")
                    else:
                        # Check buffer bounds
                        buffer = self.gltf_data["buffers"][buffer_idx]
                        byte_offset = buffer_view.get("byteOffset", 0)
                        byte_length = buffer_view.get("byteLength", 0)
                        buffer_length = buffer.get("byteLength", 0)
                        
                        if byte_offset + byte_length > buffer_length:
                            errors.append(f"BufferView {buffer_view_idx} exceeds buffer {buffer_idx} bounds")
        
        # Check skin data consistency
        for i, skin in enumerate(self.gltf_data.get("skins", [])):
            joints = skin.get("joints", [])
            if "inverseBindMatrices" in skin:
                ibm_accessor_idx = skin["inverseBindMatrices"]
                if ibm_accessor_idx < len(self.gltf_data.get("accessors", [])):
                    ibm_accessor = self.gltf_data["accessors"][ibm_accessor_idx]
                    ibm_count = ibm_accessor.get("count", 0)
                    if ibm_count != len(joints):
                        errors.append(f"Skin {i}: inverse bind matrices count ({ibm_count}) != joints count ({len(joints)})")
                else:
                    errors.append(f"Skin {i} references invalid inverseBindMatrices accessor {ibm_accessor_idx}")
        
        # Check node references
        for i, node in enumerate(self.gltf_data.get("nodes", [])):
            if "children" in node:
                for child_idx in node["children"]:
                    if child_idx >= len(self.gltf_data["nodes"]):
                        errors.append(f"Node {i} references invalid child {child_idx}")
        
        if errors:
            print("GLTF Validation Errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("GLTF validation passed")
        return True

    def preserve_original_skeleton(self, vrm_data: Dict[str, Any]) -> int:
        """Preserve the original VRM skeleton structure and return the starting index for new nodes."""
        if not vrm_data or "nodes" not in vrm_data:
            return len(self.gltf_data["nodes"])
        
        print("WARNING: Skipping original skeleton preservation to avoid buffer corruption")
        print("Generating capsule-only GLTF to ensure compatibility")
        
        # Store offsets for potential future use
        self.accessor_offset = len(self.gltf_data["accessors"])
        self.buffer_view_offset = len(self.gltf_data["bufferViews"])
        self.buffer_offset = len(self.gltf_data["buffers"])
        self.node_offset = len(self.gltf_data["nodes"])
        
        # Return current node count - we'll only add capsule nodes
        return len(self.gltf_data["nodes"])

    def generate_gltf(self, capsules: List[Dict[str, Any]], 
                     vrm_data: Dict[str, Any] = None, dzn_path: str = None) -> Dict[str, Any]:
        """Generate complete glTF from capsule data with FLAT structure (no hierarchy)."""
        print("Generating FLAT capsule structure (no hierarchy) for maximum visibility")
        
        # Create a simple root node
        if not self.gltf_data["nodes"]:
            self.gltf_data["nodes"].append({
                "name": "CapsuleRoot",
                "children": []
            })
        
        # Generate capsule meshes with flat structure - all capsules are direct children of root
        capsule_node_indices = []
        for i, capsule in enumerate(capsules):
            position = capsule['position']
            length = capsule['length']
            r1 = capsule['radius1']
            r2 = capsule['radius2']
            rotation_matrix = capsule.get('rotation_matrix')
            bone_name = capsule.get('bone_name', f"Capsule_{i}")
            
            print(f"Creating capsule {i+1}: pos={position}, len={length:.3f}, radii=({r1:.3f},{r2:.3f})")
            
            # Generate tapered capsule mesh centered at origin
            capsule_mesh = self.generate_capsule_mesh(length, r1, r2)
            
            # Add to scene with absolute world position (no hierarchy)
            node_index = self.add_capsule_to_scene(
                capsule_mesh, 
                i + 1,  # Simple sequential numbering
                position=position,
                rotation_matrix=rotation_matrix,
                bone_name=bone_name
            )
            capsule_node_indices.append(node_index)
        
        # FLAT STRUCTURE: All capsules are direct children of the root node
        self.gltf_data["nodes"][0]["children"] = capsule_node_indices
        self.gltf_data["scenes"][0]["nodes"] = [0]  # Only root node in scene
        
        print(f"Created flat structure with {len(capsule_node_indices)} capsules as direct children of root")
        
        # Finalize buffer - ensure we have valid buffer data
        if self.buffer_data:
            # Encode buffer as base64 for embedded glTF
            buffer_base64 = base64.b64encode(self.buffer_data).decode('ascii')
            self.gltf_data["buffers"].append({
                "byteLength": len(self.buffer_data),
                "uri": f"data:application/octet-stream;base64,{buffer_base64}"
            })
            print(f"Created buffer with {len(self.buffer_data)} bytes")
        else:
            print("WARNING: No buffer data generated - this may cause import errors")
        
        # Validate GLTF structure before returning
        if not self.validate_gltf_structure():
            print("WARNING: GLTF validation failed - the file may not import correctly")
        
        # Skip VRM extensions to avoid compatibility issues
        print("Skipping VRM extensions to ensure maximum compatibility")
        
        return self.gltf_data
    
    def save_gltf(self, output_path: str):
        """Save glTF to file."""
        with open(output_path, 'w') as f:
            json.dump(self.gltf_data, f, indent=2)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert MiniZinc tapered capsule optimization output to glTF format')
    parser.add_argument('input_file', help='MiniZinc solver output with capsule parameters')
    parser.add_argument('output_file', help='Output glTF file with optimized capsules')
    parser.add_argument('vrm_file', nargs='?', help='Optional input VRM model to preserve extensions')
    parser.add_argument('--scale', type=float, help='Manual scale factor to divide coordinates by (overrides auto-detection)')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output_file
    vrm_file = args.vrm_file
    manual_scale = args.scale
    
    try:
        # Read MiniZinc output
        with open(input_file, 'r') as f:
            minizinc_output = f.read()
        
        # Create generator
        generator = GLTFCapsuleGenerator()
        
        # Load VRM data if provided
        vrm_data = {}
        if vrm_file:
            vrm_data = generator.load_vrm_model(vrm_file)
            print(f"Loaded VRM model: {vrm_file}")
        
        # Parse capsule data with DZN file for bone rotations and directions
        dzn_path = "../analysis_cpsat.dzn"  # Look for DZN file in parent directory
        import os
        if not os.path.exists(dzn_path):
            dzn_path = "analysis_cpsat.dzn"  # Fallback to current directory
        capsules = generator.parse_minizinc_output(minizinc_output, manual_scale, dzn_path)
        
        if not capsules:
            print("No capsules found in MiniZinc output!")
            sys.exit(1)
        
        print(f"Found {len(capsules)} capsules:")
        for i, cap in enumerate(capsules):
            pos = cap['position']
            r1, r2 = cap['radius1'], cap['radius2']
            capsule_type = "regular" if abs(r1 - r2) < 0.01 else "tapered"
            print(f"  Capsule {i+1}: {capsule_type}, pos({pos[0]:.3f},{pos[1]:.3f},{pos[2]:.3f}), "
                  f"len={cap['length']:.3f}, radii=({r1:.3f},{r2:.3f})")
        
        # Generate glTF with hierarchy information
        gltf_data = generator.generate_gltf(capsules, vrm_data, dzn_path)
        
        # Save to file
        generator.save_gltf(output_file)
        print(f"Generated glTF file: {output_file}")
        
        # Print stats
        total_vertices = sum(gltf_data["accessors"][mesh["primitives"][0]["attributes"]["POSITION"]]["count"] 
                           for mesh in gltf_data["meshes"] if "primitives" in mesh)
        print(f"Total vertices: {total_vertices}")
        print(f"Total meshes: {len(gltf_data['meshes'])}")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find input file - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
