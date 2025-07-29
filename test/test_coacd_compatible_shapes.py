#!/usr/bin/env python3
"""
Test shapes that are compatible with CoACD by ensuring they are manifold.
"""

import sys
import numpy as np
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shape_generators import ShapeGenerator

def create_manifold_cube():
    """Create a manifold cube that CoACD can process."""
    # Define vertices of a cube
    vertices = np.array([
        [-1, -1, -1],  # 0
        [ 1, -1, -1],  # 1
        [ 1,  1, -1],  # 2
        [-1,  1, -1],  # 3
        [-1, -1,  1],  # 4
        [ 1, -1,  1],  # 5
        [ 1,  1,  1],  # 6
        [-1,  1,  1],  # 7
    ], dtype=np.float64)
    
    # Define faces (triangles) - each face is split into 2 triangles
    faces = np.array([
        # Bottom face (z = -1)
        [0, 1, 2], [0, 2, 3],
        # Top face (z = 1)
        [4, 6, 5], [4, 7, 6],
        # Front face (y = -1)
        [0, 4, 5], [0, 5, 1],
        # Back face (y = 1)
        [2, 6, 7], [2, 7, 3],
        # Left face (x = -1)
        [0, 3, 7], [0, 7, 4],
        # Right face (x = 1)
        [1, 5, 6], [1, 6, 2]
    ], dtype=np.uint32)
    
    return vertices, faces

def create_manifold_tetrahedron():
    """Create a manifold tetrahedron that CoACD can process."""
    # Define vertices of a tetrahedron
    vertices = np.array([
        [ 0,  0,  1],  # 0 - top
        [ 1,  0, -1],  # 1 - front right
        [-1,  0, -1],  # 2 - front left
        [ 0,  1, -1],  # 3 - back
    ], dtype=np.float64)
    
    # Define faces (triangles)
    faces = np.array([
        [0, 1, 2],  # bottom face
        [0, 2, 3],  # left face
        [0, 3, 1],  # right face
        [1, 3, 2],  # back face
    ], dtype=np.uint32)
    
    return vertices, faces

def test_coacd_compatibility():
    """Test if our shapes are compatible with CoACD."""
    print("Testing CoACD compatibility of shapes")
    print("=" * 50)
    
    try:
        import coacd
        print("✅ CoACD library found")
    except ImportError:
        print("❌ CoACD library not found. Please install with 'pip install coacd'")
        return False
    
    # Test 1: Simple manifold cube
    print("\n1. Testing manifold cube")
    vertices, faces = create_manifold_cube()
    print(f"   Vertices: {len(vertices)}, Faces: {len(faces)}")
    
    try:
        # Create CoACD mesh
        mesh = coacd.Mesh(vertices, faces)
        print("   ✅ Mesh created successfully")
        
        # Run CoACD decomposition
        parts = coacd.run_coacd(
            mesh=mesh,
            threshold=0.05,
            max_convex_hull=8,
            preprocess_mode="auto"
        )
        print(f"   ✅ CoACD decomposition successful: {len(parts)} parts")
    except Exception as e:
        print(f"   ❌ CoACD failed: {e}")
    
    # Test 2: Simple manifold tetrahedron
    print("\n2. Testing manifold tetrahedron")
    vertices, faces = create_manifold_tetrahedron()
    print(f"   Vertices: {len(vertices)}, Faces: {len(faces)}")
    
    try:
        # Create CoACD mesh
        mesh = coacd.Mesh(vertices, faces)
        print("   ✅ Mesh created successfully")
        
        # Run CoACD decomposition
        parts = coacd.run_coacd(
            mesh=mesh,
            threshold=0.05,
            max_convex_hull=8,
            preprocess_mode="auto"
        )
        print(f"   ✅ CoACD decomposition successful: {len(parts)} parts")
    except Exception as e:
        print(f"   ❌ CoACD failed: {e}")
    
    # Test 3: Shapes from our generator
    print("\n3. Testing shapes from ShapeGenerator")
    generator = ShapeGenerator()
    
    # Test cube
    print("   a) Testing generated cube")
    cube_data = generator.generate_cube(2.0)
    print(f"      Vertices: {len(cube_data['vertices'])}, Faces: {len(cube_data['faces'])}")
    
    # Check if our generated cube is manifold
    vertices = np.array(cube_data['vertices'], dtype=np.float64)
    faces = np.array(cube_data['faces'], dtype=np.uint32)
    
    try:
        # Create CoACD mesh
        mesh = coacd.Mesh(vertices, faces)
        print("      ✅ Mesh created successfully")
        
        # Run CoACD decomposition
        parts = coacd.run_coacd(
            mesh=mesh,
            threshold=0.05,
            max_convex_hull=8,
            preprocess_mode="auto"
        )
        print(f"      ✅ CoACD decomposition successful: {len(parts)} parts")
    except Exception as e:
        print(f"      ❌ CoACD failed: {e}")
    
    # Test sphere
    print("   b) Testing generated sphere")
    sphere_data = generator.generate_sphere(1.0, segments=8)
    print(f"      Vertices: {len(sphere_data['vertices'])}, Faces: {len(sphere_data['faces'])}")
    
    vertices = np.array(sphere_data['vertices'], dtype=np.float64)
    faces = np.array(sphere_data['faces'], dtype=np.uint32)
    
    try:
        # Create CoACD mesh
        mesh = coacd.Mesh(vertices, faces)
        print("      ✅ Mesh created successfully")
        
        # Run CoACD decomposition
        parts = coacd.run_coacd(
            mesh=mesh,
            threshold=0.05,
            max_convex_hull=16,
            preprocess_mode="auto"
        )
        print(f"      ✅ CoACD decomposition successful: {len(parts)} parts")
    except Exception as e:
        print(f"      ❌ CoACD failed: {e}")
    
    # Test cubic stroke (spline line)
    print("   c) Testing cubic stroke (spline line)")
    stroke_data = generator.generate_cubic_stroke([(0, 0, 0), (1, 1, 0), (2, 0, 1)], 0.1, 8)
    print(f"      Vertices: {len(stroke_data['vertices'])}, Faces: {len(stroke_data['faces'])}")
    
    vertices = np.array(stroke_data['vertices'], dtype=np.float64)
    faces = np.array(stroke_data['faces'], dtype=np.uint32)
    
    try:
        # Create CoACD mesh
        mesh = coacd.Mesh(vertices, faces)
        print("      ✅ Mesh created successfully")
        
        # Run CoACD decomposition
        parts = coacd.run_coacd(
            mesh=mesh,
            threshold=0.05,
            max_convex_hull=16,
            preprocess_mode="auto"
        )
        print(f"      ✅ CoACD decomposition successful: {len(parts)} parts")
    except Exception as e:
        print(f"      ❌ CoACD failed: {e}")
    
    return True

def main():
    """Run CoACD compatibility tests."""
    print("CoACD Compatibility Tests for Shape Generation")
    print("=" * 60)
    
    success = test_coacd_compatibility()
    
    print("\n" + "=" * 60)
    if success:
        print("Tests completed! Check results above.")
        return 0
    else:
        print("Tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
