import numpy as np
from typing import Dict, List, Any

class MeshDataExtractor:
    def __init__(self, gltf_data: Dict[str, Any], get_accessor_data_func):
        self.gltf_data = gltf_data
        self.get_accessor_data = get_accessor_data_func
        self.vertices: List[List[float]] = []
        self.triangles: List[List[int]] = []
        self.normals: List[List[float]] = []
        self.bone_weights: List[List[float]] = []
        self.bone_indices: List[List[int]] = []
        self.mesh_triangles: Dict[str, List[List[int]]] = {}
        self.mesh_bounds: Dict[str, Dict[str, Any]] = {}
        self.mesh_surface_areas: Dict[str, float] = {}

    def extract_mesh_data(self):
        """Extract vertex positions, triangles, normals, weights, and bone indices from meshes."""
        if "meshes" not in self.gltf_data:
            return
            
        vertex_offset = 0  # Track vertex indices across meshes
        
        for mesh_idx, mesh in enumerate(self.gltf_data["meshes"]):
            mesh_vertices = []
            mesh_triangles = []
            mesh_normals = []
            mesh_weights = []
            mesh_bone_indices = []
            
            for primitive in mesh["primitives"]:
                if "attributes" not in primitive:
                    continue
                
                primitive_start = len(mesh_vertices)
                    
                # Extract positions
                if "POSITION" in primitive["attributes"]:
                    positions = self.get_accessor_data(primitive["attributes"]["POSITION"])
                    mesh_vertices.extend(positions)
                
                # Extract normals
                if "NORMAL" in primitive["attributes"]:
                    normals = self.get_accessor_data(primitive["attributes"]["NORMAL"])
                    mesh_normals.extend(normals)
                else:
                    # Generate default normals if not present
                    mesh_normals.extend([[0.0, 1.0, 0.0]] * len(positions))
                
                # Extract triangle indices
                if "indices" in primitive:
                    indices = self.get_accessor_data(primitive["indices"])
                    # Convert to triangles and adjust for vertex offset
                    for i in range(0, len(indices), 3):
                        if i + 2 < len(indices):
                            triangle = [
                                indices[i] + vertex_offset + primitive_start,
                                indices[i + 1] + vertex_offset + primitive_start,
                                indices[i + 2] + vertex_offset + primitive_start
                            ]
                            mesh_triangles.append(triangle)
                
                # Extract bone weights and indices
                if "WEIGHTS_0" in primitive["attributes"] and "JOINTS_0" in primitive["attributes"]:
                    weights = self.get_accessor_data(primitive["attributes"]["WEIGHTS_0"])
                    joints = self.get_accessor_data(primitive["attributes"]["JOINTS_0"])
                    mesh_weights.extend(weights)
                    mesh_bone_indices.extend(joints)
                else:
                    # Fill with default values if no skinning data
                    mesh_weights.extend([[1.0, 0.0, 0.0, 0.0]] * len(positions))
                    mesh_bone_indices.extend([[0, 0, 0, 0]] * len(positions))
            
            if mesh_vertices:
                # Store global data
                self.vertices.extend(mesh_vertices)
                self.triangles.extend(mesh_triangles)
                self.normals.extend(mesh_normals)
                self.bone_weights.extend(mesh_weights)
                self.bone_indices.extend(mesh_bone_indices)
                
                # Store per-mesh triangle data
                self.mesh_triangles[f"mesh_{mesh_idx}"] = mesh_triangles
                
                # Calculate mesh bounds
                vertices_array = np.array(mesh_vertices)
                min_bounds = np.min(vertices_array, axis=0)
                max_bounds = np.max(vertices_array, axis=0)
                
                # Calculate actual surface area
                surface_area = self._calculate_surface_area(mesh_vertices, mesh_triangles, vertex_offset)
                
                self.mesh_bounds[f"mesh_{mesh_idx}"] = {
                    "min": min_bounds,
                    "max": max_bounds,
                    "center": (min_bounds + max_bounds) / 2,
                    "size": max_bounds - min_bounds,
                    "vertex_count": len(mesh_vertices),
                    "triangle_count": len(mesh_triangles),
                    "surface_area": surface_area
                }
                
                self.mesh_surface_areas[f"mesh_{mesh_idx}"] = surface_area
                vertex_offset += len(mesh_vertices)

    def _calculate_surface_area(self, vertices: List, triangles: List, vertex_offset: int) -> float:
        """Calculate actual surface area from triangle mesh data."""
        if not triangles or not vertices:
            return 0.0
        
        total_area = 0.0
        vertices_array = np.array(vertices)
        
        for triangle in triangles:
            try:
                # Adjust triangle indices for local vertex array
                v0_idx = triangle[0] - vertex_offset
                v1_idx = triangle[1] - vertex_offset
                v2_idx = triangle[2] - vertex_offset
                
                # Bounds check
                if (0 <= v0_idx < len(vertices) and 
                    0 <= v1_idx < len(vertices) and 
                    0 <= v2_idx < len(vertices)):
                    
                    # Get triangle vertices
                    v0 = np.array(vertices[v0_idx])
                    v1 = np.array(vertices[v1_idx])
                    v2 = np.array(vertices[v2_idx])
                    
                    # Calculate triangle area using cross product
                    edge1 = v1 - v0
                    edge2 = v2 - v0
                    cross = np.cross(edge1, edge2)
                    
                    # Area is half the magnitude of the cross product
                    triangle_area = 0.5 * np.linalg.norm(cross)
                    total_area += triangle_area
                    
            except (IndexError, ValueError) as e:
                # Skip invalid triangles
                continue
        
        return total_area

    def get_vertices(self) -> List[List[float]]:
        return self.vertices

    def get_triangles(self) -> List[List[int]]:
        return self.triangles

    def get_normals(self) -> List[List[float]]:
        return self.normals

    def get_bone_weights(self) -> List[List[float]]:
        return self.bone_weights

    def get_bone_indices(self) -> List[List[int]]:
        return self.bone_indices

    def get_mesh_bounds(self) -> Dict[str, Dict[str, Any]]:
        return self.mesh_bounds

    def get_mesh_surface_areas(self) -> Dict[str, float]:
        return self.mesh_surface_areas
