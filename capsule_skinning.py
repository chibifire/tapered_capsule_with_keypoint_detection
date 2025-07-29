#!/usr/bin/env python3
"""
Capsule Skinning and Vertex Painting System.
Provides weight transfer, smoothing, and vertex color generation for capsule meshes.
Uses robust_laplacian for high-quality weight smoothing.
"""

import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from scipy.spatial.distance import cdist
from scipy.sparse.linalg import spsolve

# Try to import robust_laplacian, fall back to simple implementation if not available
try:
    import robust_laplacian
    ROBUST_LAPLACIAN_AVAILABLE = True
    print("Using robust_laplacian for high-quality weight smoothing")
except ImportError:
    ROBUST_LAPLACIAN_AVAILABLE = False
    print("Warning: robust_laplacian not available, using simplified smoothing")
    print("Install with: pip install robust_laplacian")

class CapsuleSkinningSystem:
    """
    Handles weight transfer from original mesh to capsule geometry and vertex painting.
    """
    
    def __init__(self):
        self.smoothing_lambda = 0.1  # Smoothing parameter for Laplacian
        self.mollify_factor = 1e-5   # Mollification factor for robust Laplacian
        
    def transfer_weights_closest_point(self, 
                                     capsule_vertices: np.ndarray,
                                     original_vertices: np.ndarray,
                                     original_faces: np.ndarray,
                                     original_bone_weights: np.ndarray,
                                     original_bone_indices: np.ndarray,
                                     max_influences: int = 4) -> Tuple[np.ndarray, np.ndarray]:
        """
        Transfer bone weights from original mesh to capsule vertices using closest point projection.
        
        Args:
            capsule_vertices: Nx3 array of capsule vertex positions
            original_vertices: Mx3 array of original mesh vertex positions
            original_faces: Fx3 array of original mesh face indices
            original_bone_weights: Mx4 array of bone weights (4 weights per vertex)
            original_bone_indices: Mx4 array of bone indices (4 indices per vertex)
            max_influences: Maximum number of bone influences per vertex
            
        Returns:
            Tuple of (weights, indices) arrays for capsule vertices
        """
        n_capsule_verts = len(capsule_vertices)
        n_bones = np.max(original_bone_indices) + 1
        
        # Find closest original vertex for each capsule vertex
        distances = cdist(capsule_vertices, original_vertices)
        closest_indices = np.argmin(distances, axis=1)
        
        # Initialize output arrays
        capsule_weights = np.zeros((n_capsule_verts, max_influences), dtype=np.float32)
        capsule_bone_indices = np.zeros((n_capsule_verts, max_influences), dtype=np.int32)
        
        # Transfer weights from closest vertices
        for i, closest_idx in enumerate(closest_indices):
            # Get weights and indices from closest original vertex
            orig_weights = original_bone_weights[closest_idx]
            orig_indices = original_bone_indices[closest_idx]
            
            # Sort by weight (descending) and take top influences
            weight_order = np.argsort(orig_weights)[::-1]
            
            for j in range(min(max_influences, len(weight_order))):
                if orig_weights[weight_order[j]] > 0.001:  # Skip very small weights
                    capsule_weights[i, j] = orig_weights[weight_order[j]]
                    capsule_bone_indices[i, j] = orig_indices[weight_order[j]]
        
        # Normalize weights to sum to 1.0 per vertex
        row_sums = np.sum(capsule_weights, axis=1, keepdims=True)
        row_sums = np.maximum(row_sums, 1e-10)  # Avoid division by zero
        capsule_weights = capsule_weights / row_sums
        
        return capsule_weights, capsule_bone_indices
    
    def smooth_weights_robust_laplacian(self,
                                      capsule_vertices: np.ndarray,
                                      capsule_faces: np.ndarray,
                                      initial_weights: np.ndarray) -> np.ndarray:
        """
        Smooth bone weights using robust Laplacian for high-quality results.
        
        Args:
            capsule_vertices: Nx3 array of vertex positions
            capsule_faces: Fx3 array of face indices
            initial_weights: NxK array of initial bone weights
            
        Returns:
            NxK array of smoothed bone weights
        """
        if not ROBUST_LAPLACIAN_AVAILABLE:
            return self._smooth_weights_simple(capsule_vertices, capsule_faces, initial_weights)
        
        try:
            # Build high-quality Laplacian using robust_laplacian
            L, M = robust_laplacian.mesh_laplacian(
                capsule_vertices, 
                capsule_faces, 
                mollify_factor=self.mollify_factor
            )
            
            # Solve for smooth weights: (L + λM)w = Mw_initial
            A = L + self.smoothing_lambda * M
            
            # Solve for each bone separately
            smooth_weights = np.zeros_like(initial_weights)
            n_bones = initial_weights.shape[1]
            
            for bone_idx in range(n_bones):
                b = M @ initial_weights[:, bone_idx]
                smooth_weights[:, bone_idx] = spsolve(A, b)
            
            # Normalize weights to sum to 1.0 per vertex
            row_sums = np.sum(smooth_weights, axis=1, keepdims=True)
            row_sums = np.maximum(row_sums, 1e-10)
            smooth_weights = smooth_weights / row_sums
            
            # Clamp to [0, 1] range
            smooth_weights = np.clip(smooth_weights, 0.0, 1.0)
            
            return smooth_weights.astype(np.float32)
            
        except Exception as e:
            print(f"Warning: robust_laplacian smoothing failed: {e}")
            print("Falling back to simple smoothing")
            return self._smooth_weights_simple(capsule_vertices, capsule_faces, initial_weights)
    
    def _smooth_weights_simple(self,
                             capsule_vertices: np.ndarray,
                             capsule_faces: np.ndarray,
                             initial_weights: np.ndarray,
                             iterations: int = 5) -> np.ndarray:
        """
        Simple iterative weight smoothing as fallback when robust_laplacian is not available.
        
        Args:
            capsule_vertices: Nx3 array of vertex positions
            capsule_faces: Fx3 array of face indices
            initial_weights: NxK array of initial bone weights
            iterations: Number of smoothing iterations
            
        Returns:
            NxK array of smoothed bone weights
        """
        n_verts = len(capsule_vertices)
        weights = initial_weights.copy()
        
        # Build adjacency list
        adjacency = [set() for _ in range(n_verts)]
        for face in capsule_faces:
            for i in range(3):
                for j in range(3):
                    if i != j:
                        adjacency[face[i]].add(face[j])
        
        # Iterative smoothing
        for _ in range(iterations):
            new_weights = weights.copy()
            
            for i in range(n_verts):
                if len(adjacency[i]) > 0:
                    # Average with neighbors
                    neighbor_weights = np.mean([weights[j] for j in adjacency[i]], axis=0)
                    new_weights[i] = 0.7 * weights[i] + 0.3 * neighbor_weights
            
            # Normalize
            row_sums = np.sum(new_weights, axis=1, keepdims=True)
            row_sums = np.maximum(row_sums, 1e-10)
            weights = new_weights / row_sums
        
        return weights.astype(np.float32)
    
    def generate_vertex_colors(self,
                             bone_weights: np.ndarray,
                             bone_indices: np.ndarray,
                             mode: str = "bone_visualization",
                             bone_names: List[str] = None) -> np.ndarray:
        """
        Generate vertex colors for different visualization modes.
        
        Args:
            bone_weights: NxK array of bone weights
            bone_indices: NxK array of bone indices
            mode: Visualization mode ("bone_visualization", "weight_strength", "dominant_bone")
            bone_names: Optional list of bone names for color assignment
            
        Returns:
            Nx3 array of RGB colors (0-1 range)
        """
        n_vertices = len(bone_weights)
        colors = np.zeros((n_vertices, 3), dtype=np.float32)
        
        if mode == "bone_visualization":
            # Assign unique colors per bone
            unique_bones = np.unique(bone_indices[bone_weights > 0.001])
            bone_colors = self._generate_distinct_colors(len(unique_bones))
            
            for i in range(n_vertices):
                # Find dominant bone
                max_weight_idx = np.argmax(bone_weights[i])
                if bone_weights[i, max_weight_idx] > 0.001:
                    dominant_bone = bone_indices[i, max_weight_idx]
                    bone_color_idx = np.where(unique_bones == dominant_bone)[0]
                    if len(bone_color_idx) > 0:
                        colors[i] = bone_colors[bone_color_idx[0]]
        
        elif mode == "weight_strength":
            # Heat map based on total bone influence
            total_influence = np.sum(bone_weights, axis=1)
            colors = self._heat_map_colors(total_influence)
        
        elif mode == "dominant_bone_strength":
            # Color intensity based on dominant bone weight
            max_weights = np.max(bone_weights, axis=1)
            colors = self._heat_map_colors(max_weights)
        
        elif mode == "bone_count":
            # Color based on number of influencing bones
            bone_counts = np.sum(bone_weights > 0.001, axis=1)
            max_count = np.max(bone_counts)
            if max_count > 0:
                normalized_counts = bone_counts / max_count
                colors = self._heat_map_colors(normalized_counts)
        
        return colors
    
    def _generate_distinct_colors(self, n_colors: int) -> np.ndarray:
        """Generate visually distinct colors using HSV color space."""
        colors = np.zeros((n_colors, 3))
        
        for i in range(n_colors):
            hue = (i * 137.508) % 360  # Golden angle for good distribution
            saturation = 0.7 + 0.3 * (i % 2)  # Alternate saturation
            value = 0.8 + 0.2 * ((i // 2) % 2)  # Alternate brightness
            
            # Convert HSV to RGB
            colors[i] = self._hsv_to_rgb(hue / 360.0, saturation, value)
        
        return colors
    
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> np.ndarray:
        """Convert HSV color to RGB."""
        import math
        
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        i = i % 6
        
        if i == 0:
            return np.array([v, t, p])
        elif i == 1:
            return np.array([q, v, p])
        elif i == 2:
            return np.array([p, v, t])
        elif i == 3:
            return np.array([p, q, v])
        elif i == 4:
            return np.array([t, p, v])
        else:
            return np.array([v, p, q])
    
    def _heat_map_colors(self, values: np.ndarray) -> np.ndarray:
        """Generate heat map colors from blue (low) to red (high)."""
        # Normalize values to [0, 1]
        min_val = np.min(values)
        max_val = np.max(values)
        if max_val > min_val:
            normalized = (values - min_val) / (max_val - min_val)
        else:
            normalized = np.zeros_like(values)
        
        colors = np.zeros((len(values), 3))
        
        # Blue to cyan to green to yellow to red
        for i, val in enumerate(normalized):
            if val < 0.25:
                # Blue to cyan
                t = val / 0.25
                colors[i] = [0, t, 1]
            elif val < 0.5:
                # Cyan to green
                t = (val - 0.25) / 0.25
                colors[i] = [0, 1, 1 - t]
            elif val < 0.75:
                # Green to yellow
                t = (val - 0.5) / 0.25
                colors[i] = [t, 1, 0]
            else:
                # Yellow to red
                t = (val - 0.75) / 0.25
                colors[i] = [1, 1 - t, 0]
        
        return colors
    
    def prepare_skinning_data(self,
                            bone_weights: np.ndarray,
                            bone_indices: np.ndarray,
                            max_influences: int = 4) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare skinning data for glTF export (JOINTS_0 and WEIGHTS_0 attributes).
        
        Args:
            bone_weights: NxK array of bone weights
            bone_indices: NxK array of bone indices
            max_influences: Maximum influences per vertex (typically 4 for glTF)
            
        Returns:
            Tuple of (joints_data, weights_data) as uint16 and float32 arrays
        """
        n_vertices = len(bone_weights)
        
        # Prepare JOINTS_0 data (4 bone indices per vertex, uint16)
        joints_data = np.zeros((n_vertices, 4), dtype=np.uint16)
        weights_data = np.zeros((n_vertices, 4), dtype=np.float32)
        
        for i in range(n_vertices):
            # Get weights and indices for this vertex
            vertex_weights = bone_weights[i]
            vertex_indices = bone_indices[i]
            
            # Sort by weight (descending) and take top 4
            weight_order = np.argsort(vertex_weights)[::-1]
            
            # Fill up to 4 influences
            for j in range(min(4, len(weight_order))):
                if vertex_weights[weight_order[j]] > 0.001:
                    joints_data[i, j] = vertex_indices[weight_order[j]]
                    weights_data[i, j] = vertex_weights[weight_order[j]]
        
        # Normalize weights to sum to 1.0 per vertex
        row_sums = np.sum(weights_data, axis=1, keepdims=True)
        row_sums = np.maximum(row_sums, 1e-10)
        weights_data = weights_data / row_sums
        
        return joints_data, weights_data
    
    def create_skin_object(self,
                         joint_nodes: List[int],
                         inverse_bind_matrices: List[np.ndarray] = None) -> Dict[str, Any]:
        """
        Create glTF skin object for skeletal animation.
        
        Args:
            joint_nodes: List of node indices that represent joints
            inverse_bind_matrices: Optional list of 4x4 inverse bind matrices
            
        Returns:
            glTF skin object dictionary
        """
        skin = {
            "joints": joint_nodes
        }
        
        if inverse_bind_matrices:
            # Flatten matrices and add to buffer (would need buffer management)
            # For now, just store the structure
            skin["inverseBindMatrices"] = len(inverse_bind_matrices)  # Accessor index placeholder
        
        return skin
    
    def transfer_and_smooth_capsule_weights(self,
                                          capsule_vertices: np.ndarray,
                                          capsule_faces: np.ndarray,
                                          original_mesh_data: Dict[str, Any],
                                          smoothing_iterations: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Complete pipeline: transfer weights from original mesh and smooth them.
        
        Args:
            capsule_vertices: Nx3 array of capsule vertex positions
            capsule_faces: Fx3 array of capsule face indices
            original_mesh_data: Dictionary containing original mesh data
            smoothing_iterations: Number of smoothing passes
            
        Returns:
            Tuple of (smoothed_weights, bone_indices)
        """
        # Extract original mesh data
        orig_vertices = np.array(original_mesh_data['vertices'])
        orig_faces = np.array(original_mesh_data['faces'])
        orig_weights = np.array(original_mesh_data['bone_weights'])
        orig_indices = np.array(original_mesh_data['bone_indices'])
        
        print(f"Transferring weights from {len(orig_vertices)} original vertices to {len(capsule_vertices)} capsule vertices")
        
        # Step 1: Transfer weights using closest point
        initial_weights, bone_indices = self.transfer_weights_closest_point(
            capsule_vertices, orig_vertices, orig_faces, orig_weights, orig_indices
        )
        
        print(f"Initial weight transfer complete")
        
        # Step 2: Smooth weights using robust Laplacian
        smooth_weights = initial_weights
        for i in range(smoothing_iterations):
            print(f"Smoothing iteration {i+1}/{smoothing_iterations}")
            smooth_weights = self.smooth_weights_robust_laplacian(
                capsule_vertices, capsule_faces, smooth_weights
            )
        
        print(f"Weight smoothing complete")
        
        return smooth_weights, bone_indices

def main():
    """Example usage and testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Capsule Skinning System")
        print("Usage: python capsule_skinning.py <test_mode>")
        print("  test_mode: 'colors' to test color generation")
        sys.exit(1)
    
    test_mode = sys.argv[1]
    
    if test_mode == "colors":
        # Test color generation
        skinning = CapsuleSkinningSystem()
        
        # Create test data
        n_vertices = 100
        n_bones = 8
        bone_weights = np.random.random((n_vertices, 4))
        bone_weights = bone_weights / np.sum(bone_weights, axis=1, keepdims=True)
        bone_indices = np.random.randint(0, n_bones, (n_vertices, 4))
        
        # Test different color modes
        modes = ["bone_visualization", "weight_strength", "dominant_bone_strength", "bone_count"]
        
        for mode in modes:
            colors = skinning.generate_vertex_colors(bone_weights, bone_indices, mode)
            print(f"Generated {mode} colors: {colors.shape}, range: [{np.min(colors):.3f}, {np.max(colors):.3f}]")
        
        print("Color generation test complete")
    
    elif test_mode == "laplacian":
        # Test Laplacian availability
        if ROBUST_LAPLACIAN_AVAILABLE:
            print("✅ robust_laplacian is available")
            
            # Create simple test mesh (triangle)
            vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
            faces = np.array([[0, 1, 2]], dtype=np.int32)
            
            try:
                L, M = robust_laplacian.mesh_laplacian(vertices, faces)
                print(f"✅ Laplacian computation successful: L shape {L.shape}, M shape {M.shape}")
            except Exception as e:
                print(f"❌ Laplacian computation failed: {e}")
        else:
            print("❌ robust_laplacian is not available")
            print("Install with: pip install robust_laplacian")

if __name__ == "__main__":
    main()
