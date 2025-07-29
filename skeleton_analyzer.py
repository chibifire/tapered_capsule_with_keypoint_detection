import numpy as np
import math
from typing import Dict, List, Any

class SkeletonAnalyzer:
    def __init__(self, gltf_data: Dict[str, Any]):
        self.gltf_data = gltf_data
        self.joint_names: List[str] = []
        self.bone_transforms: Dict[str, np.ndarray] = {}
        self.bone_positions: Dict[str, np.ndarray] = {}
        self.bone_rotations: Dict[str, np.ndarray] = {}
        self.joint_hierarchy: Dict[str, List[str]] = {}
        self.bone_parent_map: Dict[str, str] = {}
        self.vrm_humanoid_bones: Dict[str, str] = {}
        self.bone_directions: Dict[str, np.ndarray] = {}

    def extract_skeleton(self):
        """Extract skeleton hierarchy and joint information."""
        if "nodes" not in self.gltf_data:
            return
            
        # Find skeleton root and build hierarchy
        for i, node in enumerate(self.gltf_data["nodes"]):
            name = node.get("name", f"Node_{i}")
            self.joint_names.append(name)
            
            # Extract full transformation matrix and decompose
            transform_matrix = np.eye(4)  # Default identity matrix
            
            if "matrix" in node:
                # Full 4x4 transformation matrix provided
                transform_matrix = np.array(node["matrix"]).reshape(4, 4)
            else:
                # Build transformation matrix from TRS components
                if "translation" in node:
                    transform_matrix[:3, 3] = node["translation"]
                
                if "rotation" in node:
                    # Quaternion to rotation matrix
                    qx, qy, qz, qw = node["rotation"]
                    # Convert quaternion to 3x3 rotation matrix
                    rot_matrix = self._quaternion_to_matrix(qx, qy, qz, qw)
                    transform_matrix[:3, :3] = rot_matrix
                
                if "scale" in node:
                    # Apply scale to rotation part
                    scale = np.array(node["scale"])
                    transform_matrix[:3, :3] *= scale
            
            # Store full transformation matrix
            self.bone_transforms[name] = transform_matrix
            
            # Extract position (translation component)
            self.bone_positions[name] = transform_matrix[:3, 3]
            
            # Extract rotation matrix (3x3 upper-left)
            rotation_3x3 = transform_matrix[:3, :3]
            # Normalize to remove scale effects for pure rotation
            self.bone_rotations[name] = self._normalize_rotation_matrix(rotation_3x3)
            
            # Build hierarchy
            if "children" in node:
                children_names = [
                    self.gltf_data["nodes"][child].get("name", f"Node_{child}")
                    for child in node["children"]
                ]
                self.joint_hierarchy[name] = children_names
                
                # Build parent-child mapping
                for child_name in children_names:
                    self.bone_parent_map[child_name] = name
            else:
                self.joint_hierarchy[name] = []
        
        # Extract VRM1 humanoid bone mapping
        self.vrm_humanoid_bones = {}
        if "extensions" in self.gltf_data and "VRMC_vrm" in self.gltf_data["extensions"]:
            vrm_ext = self.gltf_data["extensions"]["VRMC_vrm"]
            if "humanoid" in vrm_ext and "humanBones" in vrm_ext["humanoid"]:
                human_bones = vrm_ext["humanoid"]["humanBones"]
                for bone_name, bone_data in human_bones.items():
                    if "node" in bone_data:
                        node_idx = bone_data["node"]
                        if node_idx < len(self.joint_names):
                            self.vrm_humanoid_bones[bone_name] = self.joint_names[node_idx]
                print(f"Found {len(self.vrm_humanoid_bones)} VRM humanoid bones")
        
        # Calculate bone direction vectors after hierarchy is built
        self._calculate_bone_directions()

    def _quaternion_to_matrix(self, qx: float, qy: float, qz: float, qw: float) -> np.ndarray:
        """Convert quaternion (x, y, z, w) to 3x3 rotation matrix."""
        # Normalize quaternion
        length = math.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)
        if length > 0:
            qx /= length
            qy /= length
            qz /= length
            qw /= length
        
        # Convert to rotation matrix
        xx, yy, zz = qx*qx, qy*qy, qz*qz
        xy, xz, yz = qx*qy, qx*qz, qy*qz
        wx, wy, wz = qw*qx, qw*qy, qw*qz
        
        return np.array([
            [1 - 2*(yy + zz), 2*(xy - wz), 2*(xz + wy)],
            [2*(xy + wz), 1 - 2*(xx + zz), 2*(yz - wx)],
            [2*(xz - wy), 2*(yz + wx), 1 - 2*(xx + yy)]
        ])

    def _normalize_rotation_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """Normalize a 3x3 matrix to ensure it's a proper rotation matrix."""
        # Use SVD to extract pure rotation from scaled rotation matrix
        U, _, Vt = np.linalg.svd(matrix)
        return U @ Vt

    def _calculate_bone_directions(self):
        """Calculate bone direction vectors from parent to child joints."""
        self.bone_directions = {}
        
        for parent_name, children in self.joint_hierarchy.items():
            if not children or parent_name not in self.bone_positions:
                continue
                
            parent_pos = np.array(self.bone_positions[parent_name])
            
            for child_name in children:
                if child_name in self.bone_positions:
                    child_pos = np.array(self.bone_positions[child_name])
                    
                    # Calculate direction vector from parent to child
                    direction = child_pos - parent_pos
                    direction_length = np.linalg.norm(direction)
                    
                    if direction_length > 0.001:  # Avoid division by zero
                        # Normalize direction vector
                        normalized_direction = direction / direction_length
                        self.bone_directions[child_name] = normalized_direction
                        
                        # Also store for parent bone (pointing towards first child)
                        if parent_name not in self.bone_directions:
                            self.bone_directions[parent_name] = normalized_direction

    def get_joint_names(self) -> List[str]:
        return self.joint_names

    def get_bone_positions(self) -> Dict[str, np.ndarray]:
        return self.bone_positions

    def get_bone_rotations(self) -> Dict[str, np.ndarray]:
        return self.bone_rotations

    def get_joint_hierarchy(self) -> Dict[str, List[str]]:
        return self.joint_hierarchy

    def get_bone_parent_map(self) -> Dict[str, str]:
        return self.bone_parent_map

    def get_vrm_humanoid_bones(self) -> Dict[str, str]:
        return self.vrm_humanoid_bones

    def get_bone_directions(self) -> Dict[str, np.ndarray]:
        return self.bone_directions
