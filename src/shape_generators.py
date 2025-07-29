#!/usr/bin/env python3
"""
Shape generation utilities for testing tapered capsule optimization.
Generates various geometric shapes for testing the pipeline.
"""

import numpy as np
from typing import Tuple, List, Dict, Any

class ShapeGenerator:
    """Generate various geometric shapes for testing."""
    
    @staticmethod
    def generate_cuboid(width: float, height: float, depth: float, 
                       center: Tuple[float, float, float] = (0, 0, 0)) -> Dict[str, Any]:
        """Generate a cuboid with specified dimensions."""
        cx, cy, cz = center
        
        # Define vertices of a cuboid
        vertices = np.array([
            # Bottom face
            [cx - width/2, cy - height/2, cz - depth/2],  # 0
            [cx + width/2, cy - height/2, cz - depth/2],  # 1
            [cx + width/2, cy - height/2, cz + depth/2],  # 2
            [cx - width/2, cy - height/2, cz + depth/2],  # 3
            # Top face
            [cx - width/2, cy + height/2, cz - depth/2],  # 4
            [cx + width/2, cy + height/2, cz - depth/2],  # 5
            [cx + width/2, cy + height/2, cz + depth/2],  # 6
            [cx - width/2, cy + height/2, cz + depth/2],  # 7
        ])
        
        # Define faces (triangles) - each face is split into 2 triangles
        faces = np.array([
            # Bottom face
            [0, 1, 2], [0, 2, 3],
            # Top face
            [4, 6, 5], [4, 7, 6],
            # Front face
            [0, 4, 5], [0, 5, 1],
            # Back face
            [2, 6, 7], [2, 7, 3],
            # Left face
            [0, 3, 7], [0, 7, 4],
            # Right face
            [1, 5, 6], [1, 6, 2]
        ])
        
        return {
            'vertices': vertices,
            'faces': faces,
            'bounds': np.array([[cx - width/2, cy - height/2, cz - depth/2],
                               [cx + width/2, cy + height/2, cz + depth/2]])
        }
    
    @staticmethod
    def generate_cube(size: float, center: Tuple[float, float, float] = (0, 0, 0)) -> Dict[str, Any]:
        """Generate a cube with specified size."""
        return ShapeGenerator.generate_cuboid(size, size, size, center)
    
    @staticmethod
    def generate_cylinder(radius: float, height: float, 
                         center: Tuple[float, float, float] = (0, 0, 0),
                         segments: int = 32) -> Dict[str, Any]:
        """Generate a cylinder with specified radius and height."""
        cx, cy, cz = center
        
        vertices = []
        faces = []
        
        # Top and bottom center points
        top_center = np.array([cx, cy + height/2, cz])
        bottom_center = np.array([cx, cy - height/2, cz])
        
        vertices.append(top_center)
        vertices.append(bottom_center)
        top_center_idx = 0
        bottom_center_idx = 1
        
        # Generate vertices around the circumference
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = cx + radius * np.cos(angle)
            z = cz + radius * np.sin(angle)
            
            # Top ring
            vertices.append(np.array([x, cy + height/2, z]))
            # Bottom ring
            vertices.append(np.array([x, cy - height/2, z]))
        
        # Generate faces
        # Top cap
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([top_center_idx, 
                         2 + 2*i, 
                         2 + 2*next_i])
        
        # Bottom cap
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([bottom_center_idx, 
                         2 + 2*next_i + 1, 
                         2 + 2*i + 1])
        
        # Side faces
        for i in range(segments):
            next_i = (i + 1) % segments
            # Two triangles per quad
            faces.append([2 + 2*i, 2 + 2*i + 1, 2 + 2*next_i])
            faces.append([2 + 2*next_i, 2 + 2*i + 1, 2 + 2*next_i + 1])
        
        vertices = np.array(vertices)
        faces = np.array(faces)
        
        return {
            'vertices': vertices,
            'faces': faces,
            'bounds': np.array([[cx - radius, cy - height/2, cz - radius],
                               [cx + radius, cy + height/2, cz + radius]])
        }
    
    @staticmethod
    def generate_cone(base_radius: float, height: float,
                     center: Tuple[float, float, float] = (0, 0, 0),
                     segments: int = 32) -> Dict[str, Any]:
        """Generate a cone with specified base radius and height."""
        cx, cy, cz = center
        
        vertices = []
        faces = []
        
        # Apex and base center points
        apex = np.array([cx, cy + height/2, cz])
        base_center = np.array([cx, cy - height/2, cz])
        
        vertices.append(apex)
        vertices.append(base_center)
        apex_idx = 0
        base_center_idx = 1
        
        # Generate vertices around the base circumference
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = cx + base_radius * np.cos(angle)
            z = cz + base_radius * np.sin(angle)
            vertices.append(np.array([x, cy - height/2, z]))
        
        # Generate faces
        # Base cap
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([base_center_idx, 
                         2 + next_i, 
                         2 + i])
        
        # Side faces
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([apex_idx, 2 + i, 2 + next_i])
        
        vertices = np.array(vertices)
        faces = np.array(faces)
        
        return {
            'vertices': vertices,
            'faces': faces,
            'bounds': np.array([[cx - base_radius, cy - height/2, cz - base_radius],
                               [cx + base_radius, cy + height/2, cz + base_radius]])
        }
    
    @staticmethod
    def generate_ellipsoid(a: float, b: float, c: float,
                          center: Tuple[float, float, float] = (0, 0, 0),
                          segments: int = 16) -> Dict[str, Any]:
        """Generate an ellipsoid with semi-axes a, b, c."""
        cx, cy, cz = center
        
        vertices = []
        faces = []
        
        # Generate vertices using spherical coordinates
        for i in range(segments + 1):
            phi = np.pi * i / segments  # Latitude (0 to π)
            for j in range(segments + 1):
                theta = 2 * np.pi * j / segments  # Longitude (0 to 2π)
                
                x = cx + a * np.sin(phi) * np.cos(theta)
                y = cy + b * np.cos(phi)
                z = cz + c * np.sin(phi) * np.sin(theta)
                
                vertices.append(np.array([x, y, z]))
        
        # Generate faces
        for i in range(segments):
            for j in range(segments):
                # Indices of the four vertices of a quad
                i1 = i * (segments + 1) + j
                i2 = i * (segments + 1) + (j + 1)
                i3 = (i + 1) * (segments + 1) + j
                i4 = (i + 1) * (segments + 1) + (j + 1)
                
                # Two triangles per quad
                faces.append([i1, i3, i2])
                faces.append([i2, i3, i4])
        
        vertices = np.array(vertices)
        faces = np.array(faces)
        
        return {
            'vertices': vertices,
            'faces': faces,
            'bounds': np.array([[cx - a, cy - b, cz - c],
                               [cx + a, cy + b, cz + c]])
        }
    
    @staticmethod
    def generate_sphere(radius: float, center: Tuple[float, float, float] = (0, 0, 0),
                       segments: int = 16) -> Dict[str, Any]:
        """Generate a sphere with specified radius."""
        return ShapeGenerator.generate_ellipsoid(radius, radius, radius, center, segments)
    
    @staticmethod
    def generate_markoid(a: float, b: float, c: float, power: float = 2.0,
                        center: Tuple[float, float, float] = (0, 0, 0),
                        segments: int = 16) -> Dict[str, Any]:
        """Generate a super ellipsoid (markoid) with variable power."""
        cx, cy, cz = center
        
        vertices = []
        faces = []
        
        # Generate vertices using modified spherical coordinates for super ellipsoids
        for i in range(segments + 1):
            phi = np.pi * i / segments
            for j in range(segments + 1):
                theta = 2 * np.pi * j / segments
                
                # Super ellipsoid parametrization
                # sign(sin(phi)) * |sin(phi)|^(2/n) * sign(cos(theta)) * |cos(theta)|^(2/n)
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)
                cos_theta = np.cos(theta)
                sin_theta = np.sin(theta)
                
                # Apply power transformation
                sign_sin_phi = 1 if sin_phi >= 0 else -1
                sign_cos_phi = 1 if cos_phi >= 0 else -1
                sign_cos_theta = 1 if cos_theta >= 0 else -1
                sign_sin_theta = 1 if sin_theta >= 0 else -1
                
                x_factor = sign_sin_phi * (abs(sin_phi) ** (2/power)) * sign_cos_theta * (abs(cos_theta) ** (2/power))
                y_factor = sign_cos_phi * (abs(cos_phi) ** (2/power))
                z_factor = sign_sin_phi * (abs(sin_phi) ** (2/power)) * sign_sin_theta * (abs(sin_theta) ** (2/power))
                
                x = cx + a * x_factor
                y = cy + b * y_factor
                z = cz + c * z_factor
                
                vertices.append(np.array([x, y, z]))
        
        # Generate faces (same as ellipsoid)
        for i in range(segments):
            for j in range(segments):
                i1 = i * (segments + 1) + j
                i2 = i * (segments + 1) + (j + 1)
                i3 = (i + 1) * (segments + 1) + j
                i4 = (i + 1) * (segments + 1) + (j + 1)
                
                faces.append([i1, i3, i2])
                faces.append([i2, i3, i4])
        
        vertices = np.array(vertices)
        faces = np.array(faces)
        
        return {
            'vertices': vertices,
            'faces': faces,
            'bounds': np.array([[cx - a, cy - b, cz - c],
                               [cx + a, cy + b, cz + c]])
        }
    
    @staticmethod
    def generate_triangular_prism(width: float, height: float, depth: float,
                                 center: Tuple[float, float, float] = (0, 0, 0)) -> Dict[str, Any]:
        """Generate a triangular prism."""
        cx, cy, cz = center
        
        vertices = []
        faces = []
        
        # Define the triangular base points (in XY plane)
        h = np.sqrt(3) / 2 * width  # Height of equilateral triangle
        
        # Front triangular face
        vertices.append(np.array([cx, cy + h/3, cz + depth/2]))  # Top
        vertices.append(np.array([cx - width/2, cy - 2*h/3, cz + depth/2]))  # Bottom left
        vertices.append(np.array([cx + width/2, cy - 2*h/3, cz + depth/2]))  # Bottom right
        
        # Back triangular face
        vertices.append(np.array([cx, cy + h/3, cz - depth/2]))  # Top
        vertices.append(np.array([cx - width/2, cy - 2*h/3, cz - depth/2]))  # Bottom left
        vertices.append(np.array([cx + width/2, cy - 2*h/3, cz - depth/2]))  # Bottom right
        
        # Faces
        # Front face
        faces.append([0, 1, 2])
        # Back face
        faces.append([3, 5, 4])
        # Side faces
        faces.append([0, 3, 4])
        faces.append([0, 4, 1])
        faces.append([1, 4, 5])
        faces.append([1, 5, 2])
        faces.append([2, 5, 3])
        faces.append([2, 3, 0])
        
        vertices = np.array(vertices)
        faces = np.array(faces)
        
        return {
            'vertices': vertices,
            'faces': faces,
            'bounds': np.array([[cx - width/2, cy - 2*h/3, cz - depth/2],
                               [cx + width/2, cy + h/3, cz + depth/2]])
        }
    
    @staticmethod
    def generate_pyramid(base_width: float, base_depth: float, height: float,
                        center: Tuple[float, float, float] = (0, 0, 0)) -> Dict[str, Any]:
        """Generate a rectangular pyramid."""
        cx, cy, cz = center
        
        vertices = []
        faces = []
        
        # Base vertices (square base)
        vertices.append(np.array([cx - base_width/2, cy - height/2, cz - base_depth/2]))  # 0
        vertices.append(np.array([cx + base_width/2, cy - height/2, cz - base_depth/2]))  # 1
        vertices.append(np.array([cx + base_width/2, cy - height/2, cz + base_depth/2]))  # 2
        vertices.append(np.array([cx - base_width/2, cy - height/2, cz + base_depth/2]))  # 3
        
        # Apex
        vertices.append(np.array([cx, cy + height/2, cz]))  # 4
        
        # Faces
        # Base
        faces.append([0, 2, 1])
        faces.append([0, 3, 2])
        # Sides
        faces.append([0, 1, 4])
        faces.append([1, 2, 4])
        faces.append([2, 3, 4])
        faces.append([3, 0, 4])
        
        vertices = np.array(vertices)
        faces = np.array(faces)
        
        return {
            'vertices': vertices,
            'faces': faces,
            'bounds': np.array([[cx - base_width/2, cy - height/2, cz - base_depth/2],
                               [cx + base_width/2, cy + height/2, cz + base_depth/2]])
        }
    
    @staticmethod
    def generate_torus(major_radius: float, minor_radius: float,
                      center: Tuple[float, float, float] = (0, 0, 0),
                      major_segments: int = 32, minor_segments: int = 16) -> Dict[str, Any]:
        """Generate a torus (donut shape)."""
        cx, cy, cz = center
        
        vertices = []
        faces = []
        
        # Generate vertices
        for i in range(major_segments):
            major_angle = 2 * np.pi * i / major_segments
            major_x = (major_radius + minor_radius) * np.cos(major_angle)
            major_z = (major_radius + minor_radius) * np.sin(major_angle)
            
            for j in range(minor_segments):
                minor_angle = 2 * np.pi * j / minor_segments
                
                # Position on the tube
                x = (major_radius + minor_radius * np.cos(minor_angle)) * np.cos(major_angle)
                y = minor_radius * np.sin(minor_angle)
                z = (major_radius + minor_radius * np.cos(minor_angle)) * np.sin(major_angle)
                
                vertices.append(np.array([cx + x, cy + y, cz + z]))
        
        # Generate faces
        for i in range(major_segments):
            next_i = (i + 1) % major_segments
            for j in range(minor_segments):
                next_j = (j + 1) % minor_segments
                
                # Indices of the four vertices of a quad
                i1 = i * minor_segments + j
                i2 = i * minor_segments + next_j
                i3 = next_i * minor_segments + j
                i4 = next_i * minor_segments + next_j
                
                # Two triangles per quad
                faces.append([i1, i3, i2])
                faces.append([i2, i3, i4])
        
        vertices = np.array(vertices)
        faces = np.array(faces)
        
        bounds_size = major_radius + minor_radius
        return {
            'vertices': vertices,
            'faces': faces,
            'bounds': np.array([[cx - bounds_size, cy - minor_radius, cz - bounds_size],
                               [cx + bounds_size, cy + minor_radius, cz + bounds_size]])
        }
    
    @staticmethod
    def generate_biscuit(radius: float, thickness: float,
                        center: Tuple[float, float, float] = (0, 0, 0),
                        segments: int = 32) -> Dict[str, Any]:
        """Generate a biscuit shape (cylinder with rounded edges)."""
        cx, cy, cz = center
        
        vertices = []
        faces = []
        
        # Generate vertices for top and bottom circles with rounded edges
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = cx + radius * np.cos(angle)
            z = cz + radius * np.sin(angle)
            
            # Top circle (slightly inset for rounded edge)
            vertices.append(np.array([x, cy + thickness/2, z]))
            # Bottom circle (slightly inset for rounded edge)
            vertices.append(np.array([x, cy - thickness/2, z]))
        
        # Add center points for top and bottom
        vertices.append(np.array([cx, cy + thickness/2, cz]))  # Top center
        vertices.append(np.array([cx, cy - thickness/2, cz]))  # Bottom center
        
        top_center_idx = len(vertices) - 2
        bottom_center_idx = len(vertices) - 1
        
        # Generate faces
        # Top cap
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([top_center_idx, 2*i, 2*next_i])
        
        # Bottom cap
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([bottom_center_idx, 2*next_i + 1, 2*i + 1])
        
        # Side faces
        for i in range(segments):
            next_i = (i + 1) % segments
            # Two triangles per quad
            faces.append([2*i, 2*i + 1, 2*next_i])
            faces.append([2*next_i, 2*i + 1, 2*next_i + 1])
        
        vertices = np.array(vertices)
        faces = np.array(faces)
        
        return {
            'vertices': vertices,
            'faces': faces,
            'bounds': np.array([[cx - radius, cy - thickness/2, cz - radius],
                               [cx + radius, cy + thickness/2, cz + radius]])
        }
    
    @staticmethod
    def generate_cubic_stroke(points: List[Tuple[float, float, float]], 
                             radius: float = 0.1,
                             segments: int = 8) -> Dict[str, Any]:
        """Generate a cubic stroke (spline line) following a series of control points."""
        if len(points) < 2:
            raise ValueError("Need at least 2 points to create a stroke")
        
        vertices = []
        faces = []
        
        # For each segment between points, create a cylindrical section
        for i in range(len(points) - 1):
            p1 = np.array(points[i])
            p2 = np.array(points[i + 1])
            
            # Calculate direction vector
            direction = p2 - p1
            length = np.linalg.norm(direction)
            if length == 0:
                continue
                
            direction = direction / length
            
            # Create orthogonal vectors for the circular cross-section
            # Find a vector not parallel to direction
            if abs(direction[0]) < 0.9:
                arbitrary = np.array([1, 0, 0])
            else:
                arbitrary = np.array([0, 1, 0])
                
            # Create orthogonal vectors using cross product
            up = np.cross(direction, arbitrary)
            up = up / np.linalg.norm(up)
            right = np.cross(direction, up)
            
            # Generate circular vertices around this segment
            segment_vertices_start = len(vertices)
            
            # Add vertices for circular cross-section at start and end points
            for j in range(segments):
                angle = 2 * np.pi * j / segments
                offset = radius * (np.cos(angle) * right + np.sin(angle) * up)
                
                # Start point circle
                vertices.append(p1 + offset)
                # End point circle
                vertices.append(p2 + offset)
            
            # Connect vertices to form cylindrical surface
            for j in range(segments):
                next_j = (j + 1) % segments
                # Two triangles per quad
                faces.append([segment_vertices_start + 2*j, 
                             segment_vertices_start + 2*next_j, 
                             segment_vertices_start + 2*j + 1])
                faces.append([segment_vertices_start + 2*j + 1, 
                             segment_vertices_start + 2*next_j, 
                             segment_vertices_start + 2*next_j + 1])
        
        vertices = np.array(vertices)
        faces = np.array(faces)
        
        # Calculate bounds
        if len(vertices) > 0:
            bounds = np.array([np.min(vertices, axis=0) - radius,
                              np.max(vertices, axis=0) + radius])
        else:
            bounds = np.array([[-radius, -radius, -radius],
                              [radius, radius, radius]])
        
        return {
            'vertices': vertices,
            'faces': faces,
            'bounds': bounds
        }

def create_mock_mesh(vertices: np.ndarray, faces: np.ndarray, bounds: np.ndarray) -> Any:
    """Create a mock mesh object compatible with the pipeline."""
    
    class MockMesh:
        def __init__(self, vertices, faces, bounds):
            self.vertices = vertices
            self.faces = faces
            self.bounds = bounds
            
        def sample(self, num_points, return_index=False):
            # Sample points within bounds
            points = np.random.uniform(self.bounds[0], self.bounds[1], (num_points, 3))
            if return_index:
                return points, np.arange(num_points)
            return points
    
    return MockMesh(vertices, faces, bounds)


class CoACDCompatibleMesh:
    """A mesh class that's compatible with CoACD library."""
    
    def __init__(self, vertices: np.ndarray, faces: np.ndarray):
        self.vertices = vertices
        self.faces = faces
        self.bounds = np.array([
            np.min(vertices, axis=0),
            np.max(vertices, axis=0)
        ])
    
    def sample(self, num_points, return_index=False):
        """Sample points within the mesh bounds."""
        points = np.random.uniform(self.bounds[0], self.bounds[1], (num_points, 3))
        if return_index:
            return points, np.arange(num_points)
        return points

# Example usage:
if __name__ == "__main__":
    # Test shape generation
    generator = ShapeGenerator()
    
    # Generate a cube
    cube_data = generator.generate_cube(2.0)
    print(f"Cube: {len(cube_data['vertices'])} vertices, {len(cube_data['faces'])} faces")
    
    # Generate a sphere
    sphere_data = generator.generate_sphere(1.0, segments=8)
    print(f"Sphere: {len(sphere_data['vertices'])} vertices, {len(sphere_data['faces'])} faces")
