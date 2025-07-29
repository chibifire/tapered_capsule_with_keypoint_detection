#!/usr/bin/env python3
"""
Test shapes through CoACD decomposition directly.
This test focuses on verifying that our generated shapes are compatible with CoACD.
"""

import sys
import numpy as np
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shape_generators import ShapeGenerator

def test_shape_with_coacd(shape_name: str, vertices: np.ndarray, faces: np.ndarray):
    """Test a shape with CoACD directly."""
    print(f"\nTesting {shape_name} with CoACD")
    print("-" * 40)
    
    try:
        import coacd
        
        # Print shape info
        print(f"  Vertices: {len(vertices)}")
        print(f"  Faces: {len(faces)}")
        
        # Create CoACD mesh
        mesh = coacd.Mesh(vertices, faces)
        print("  ✅ Mesh created successfully")
        
        # Run CoACD decomposition
        parts = coacd.run_coacd(
            mesh=mesh,
            threshold=0.05,
            max_convex_hull=16,
            preprocess_mode="auto",
            merge=True
        )
        
        print(f"  ✅ CoACD decomposition successful: {len(parts)} parts")
        return True
        
    except ImportError:
        print("  ❌ CoACD library not found")
        return False
    except Exception as e:
        print(f"  ❌ CoACD failed: {e}")
        return False

def test_all_shapes():
    """Test all requested shapes with CoACD."""
    print("Testing All Requested Shapes with CoACD")
    print("=" * 50)
    
    generator = ShapeGenerator()
    
    # Test results
    results = []
    
    # 1. Platonic Solids
    print("1. PLATONIC SOLIDS")
    
    # Tetrahedron (4 faces)
    print("   a) Tetrahedron")
    vertices, faces = create_tetrahedron()
    result = test_shape_with_coacd("Tetrahedron", vertices, faces)
    results.append(("Tetrahedron", result))
    
    # Cube (6 faces) - using our generator
    print("   b) Cube")
    cube_data = generator.generate_cube(2.0)
    vertices = np.array(cube_data['vertices'], dtype=np.float64)
    faces = np.array(cube_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Cube", vertices, faces)
    results.append(("Cube", result))
    
    # Octahedron (8 faces)
    print("   c) Octahedron")
    vertices, faces = create_octahedron()
    result = test_shape_with_coacd("Octahedron", vertices, faces)
    results.append(("Octahedron", result))
    
    # 2. Other Requested Shapes
    print("\n2. OTHER REQUESTED SHAPES")
    
    # Cylinders
    print("   a) Cylinder")
    cylinder_data = generator.generate_cylinder(1.0, 2.0, segments=16)
    vertices = np.array(cylinder_data['vertices'], dtype=np.float64)
    faces = np.array(cylinder_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Cylinder", vertices, faces)
    results.append(("Cylinder", result))
    
    # Cones
    print("   b) Cone")
    cone_data = generator.generate_cone(1.0, 2.0, segments=16)
    vertices = np.array(cone_data['vertices'], dtype=np.float64)
    faces = np.array(cone_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Cone", vertices, faces)
    results.append(("Cone", result))
    
    # Cuboids
    print("   c) Cuboid")
    cuboid_data = generator.generate_cuboid(1.5, 2.0, 1.0)
    vertices = np.array(cuboid_data['vertices'], dtype=np.float64)
    faces = np.array(cuboid_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Cuboid", vertices, faces)
    results.append(("Cuboid", result))
    
    # Ellipsoids
    print("   d) Ellipsoid")
    ellipsoid_data = generator.generate_ellipsoid(1.0, 1.5, 0.8, segments=12)
    vertices = np.array(ellipsoid_data['vertices'], dtype=np.float64)
    faces = np.array(ellipsoid_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Ellipsoid", vertices, faces)
    results.append(("Ellipsoid", result))
    
    # Triangular prisms
    print("   e) Triangular Prism")
    prism_data = generator.generate_triangular_prism(1.5, 2.0, 1.0)
    vertices = np.array(prism_data['vertices'], dtype=np.float64)
    faces = np.array(prism_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Triangular Prism", vertices, faces)
    results.append(("Triangular Prism", result))
    
    # Donuts (torus)
    print("   f) Donut (Torus)")
    torus_data = generator.generate_torus(1.5, 0.5, major_segments=12, minor_segments=8)
    vertices = np.array(torus_data['vertices'], dtype=np.float64)
    faces = np.array(torus_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Donut", vertices, faces)
    results.append(("Donut", result))
    
    # Biscuits
    print("   g) Biscuit")
    biscuit_data = generator.generate_biscuit(1.0, 0.3, segments=12)
    vertices = np.array(biscuit_data['vertices'], dtype=np.float64)
    faces = np.array(biscuit_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Biscuit", vertices, faces)
    results.append(("Biscuit", result))
    
    # Markoids (super ellipsoids)
    print("   h) Markoid (Super Ellipsoid)")
    markoid_data = generator.generate_markoid(1.2, 1.0, 0.8, power=2.5, segments=12)
    vertices = np.array(markoid_data['vertices'], dtype=np.float64)
    faces = np.array(markoid_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Markoid", vertices, faces)
    results.append(("Markoid", result))
    
    # Pyramids
    print("   i) Pyramid")
    pyramid_data = generator.generate_pyramid(1.5, 1.5, 2.0)
    vertices = np.array(pyramid_data['vertices'], dtype=np.float64)
    faces = np.array(pyramid_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Pyramid", vertices, faces)
    results.append(("Pyramid", result))
    
    # Cubic Strokes (Spline Lines)
    print("   j) Cubic Stroke (Spline Line)")
    stroke_data = generator.generate_cubic_stroke([(0, 0, 0), (1, 1, 0), (2, 0, 1)], 0.1, 8)
    vertices = np.array(stroke_data['vertices'], dtype=np.float64)
    faces = np.array(stroke_data['faces'], dtype=np.uint32)
    result = test_shape_with_coacd("Cubic Stroke", vertices, faces)
    results.append(("Cubic Stroke", result))
    
    return results

def create_tetrahedron():
    """Create a regular tetrahedron."""
    # Vertices of a regular tetrahedron
    vertices = np.array([
        [ 1,  1,  1],  # 0
        [ 1, -1, -1],  # 1
        [-1,  1, -1],  # 2
        [-1, -1,  1],  # 3
    ], dtype=np.float64) / np.sqrt(3)  # Normalize to unit edge length
    
    # Faces (triangles)
    faces = np.array([
        [0, 1, 2],  # Face 1
        [0, 2, 3],  # Face 2
        [0, 3, 1],  # Face 3
        [1, 3, 2],  # Face 4
    ], dtype=np.uint32)
    
    return vertices, faces

def create_octahedron():
    """Create a regular octahedron."""
    # Vertices of a regular octahedron
    vertices = np.array([
        [ 1,  0,  0],  # 0
        [-1,  0,  0],  # 1
        [ 0,  1,  0],  # 2
        [ 0, -1,  0],  # 3
        [ 0,  0,  1],  # 4
        [ 0,  0, -1],  # 5
    ], dtype=np.float64)
    
    # Faces (triangles)
    faces = np.array([
        [0, 2, 4],  # Face 1
        [0, 4, 3],  # Face 2
        [0, 3, 5],  # Face 3
        [0, 5, 2],  # Face 4
        [1, 4, 2],  # Face 5
        [1, 3, 4],  # Face 6
        [1, 5, 3],  # Face 7
        [1, 2, 5],  # Face 8
    ], dtype=np.uint32)
    
    return vertices, faces

def main():
    """Run all shape tests with CoACD."""
    print("Shape Tests with CoACD Decomposition")
    print("=" * 50)
    
    # Check if CoACD is available
    try:
        import coacd
        print("✅ CoACD library found")
    except ImportError:
        print("❌ CoACD library not found. Please install with 'pip install coacd'")
        return 1
    
    # Run all tests
    results = test_all_shapes()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for shape_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {shape_name}")
        if success:
            passed += 1
    
    print("-" * 50)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
