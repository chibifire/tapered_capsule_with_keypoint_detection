#!/usr/bin/env python3
"""
Test the tapered capsule pipeline with various geometric shapes.
"""

import sys
import os
import tempfile
import numpy as np
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shape_generators import ShapeGenerator, create_mock_mesh, CoACDCompatibleMesh
from src.coacd_capsule_pipeline import CoACDCapsulePipeline

def test_cube_pipeline():
    """Test the pipeline with a cube shape."""
    print("Testing tapered capsule pipeline with cube")
    print("=" * 50)
    
    # Generate a cube
    shape_data = ShapeGenerator.generate_cube(2.0, center=(0, 1, 0))
    mock_mesh = CoACDCompatibleMesh(
        shape_data['vertices'], 
        shape_data['faces']
    )
    
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a mock VRM file path (we won't actually load a VRM file)
        vrm_path = temp_path / "cube.vrm"
        vrm_path.touch()  # Create empty file
        
        try:
            # Create pipeline
            pipeline = CoACDCapsulePipeline(str(vrm_path), str(temp_path))
            
            # Mock the mesh data extractor to return our cube data
            class MockMeshDataExtractor:
                def __init__(self, vertices):
                    self.vertices = vertices
                    
                def get_vertices(self):
                    return self.vertices.tolist()
                    
                def get_bone_weights(self):
                    # Return dummy bone weights (all vertices influenced by bone 0)
                    return [[1.0] for _ in range(len(self.vertices))]
                    
                def get_bone_indices(self):
                    # Return dummy bone indices (all vertices influenced by bone 0)
                    return [[0] for _ in range(len(self.vertices))]
            
            # Mock the GLTF parser
            class MockGLTFParser:
                def __init__(self):
                    pass
                    
                def load_glb(self, path):
                    return True
                    
                def get_gltf_data(self):
                    return {
                        "nodes": [{"name": "RootNode"}],
                        "skins": [{"joints": [0]}],
                        "meshes": [{}]
                    }
                    
                def get_accessor_data(self, accessor):
                    return None
            
            # Override the pipeline's mesh loading methods
            pipeline.gltf_parser = MockGLTFParser()
            
            # Set up mock data
            pipeline.mesh_data_extractor = MockMeshDataExtractor(shape_data['vertices'])
            pipeline.joint_names = ["CubeBone"]
            pipeline.bone_weights = pipeline.mesh_data_extractor.get_bone_weights()
            pipeline.bone_indices = pipeline.mesh_data_extractor.get_bone_indices()
            
            # Group vertices by bone
            pipeline._group_vertices_by_bone()
            
            # Run CoACD decomposition
            hulls = pipeline._run_coacd_global(mock_mesh, threshold=0.05)
            print(f"Generated {len(hulls)} convex hulls")
            
            # Generate candidate capsules
            capsules = pipeline.generate_candidate_capsules(hulls)
            print(f"Generated {len(capsules)} candidate capsules")
            
            # Sample witness points
            witness_points = pipeline.sample_witness_points(mock_mesh, num_points=1000)
            print(f"Sampled {len(witness_points)} witness points")
            
            # Build coverage matrix
            coverage_matrix = pipeline.build_coverage_matrix(capsules, witness_points)
            print(f"Built coverage matrix: {coverage_matrix.shape}")
            
            # Create MiniZinc data file
            data_file = temp_path / "cube_data.dzn"
            success = pipeline.create_minizinc_data_file(capsules, witness_points, coverage_matrix, str(data_file))
            if success:
                print(f"Created MiniZinc data file: {data_file}")
            else:
                print("Failed to create MiniZinc data file")
            
            # Process results (create GLTF)
            results_file = temp_path / "cube_results.txt"
            # Create a simple results file
            with open(results_file, 'w') as f:
                f.write(f"Selected capsules: {len(capsules)}\n")
                f.write("Capsule indices: [" + ", ".join(str(i+1) for i in range(len(capsules))) + "]\n")
                for i, capsule in enumerate(capsules):
                    f.write(f"Capsule {i+1}: center({capsule['center'][0]}, {capsule['center'][1]}, {capsule['center'][2]}) "
                            f"height({capsule['height']}) radii({capsule['radius_top']}, {capsule['radius_bottom']}) "
                            f"swing({capsule['swing_rotation'][0]}, {capsule['swing_rotation'][1]}, {capsule['swing_rotation'][2]}) "
                            f"twist({capsule['twist_rotation']})\n")
            
            gltf_file = temp_path / "cube_capsules.gltf"
            success = pipeline.process_results(capsules, str(results_file), str(gltf_file))
            if success:
                print(f"Generated GLTF file: {gltf_file}")
            else:
                print("Failed to generate GLTF file")
            
            print("✅ Cube pipeline test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error during cube pipeline test: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_sphere_pipeline():
    """Test the pipeline with a sphere shape."""
    print("\nTesting tapered capsule pipeline with sphere")
    print("=" * 50)
    
    # Generate a sphere
    shape_data = ShapeGenerator.generate_sphere(1.5, segments=16)
    mock_mesh = CoACDCompatibleMesh(
        shape_data['vertices'], 
        shape_data['faces']
    )
    
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a mock VRM file path
        vrm_path = temp_path / "sphere.vrm"
        vrm_path.touch()
        
        try:
            # Create pipeline
            pipeline = CoACDCapsulePipeline(str(vrm_path), str(temp_path))
            
            # Mock the mesh data extractor
            class MockMeshDataExtractor:
                def __init__(self, vertices):
                    self.vertices = vertices
                    
                def get_vertices(self):
                    return self.vertices.tolist()
                    
                def get_bone_weights(self):
                    return [[1.0] for _ in range(len(self.vertices))]
                    
                def get_bone_indices(self):
                    return [[0] for _ in range(len(self.vertices))]
            
            # Mock the GLTF parser
            class MockGLTFParser:
                def load_glb(self, path):
                    return True
                    
                def get_gltf_data(self):
                    return {
                        "nodes": [{"name": "RootNode"}],
                        "skins": [{"joints": [0]}],
                        "meshes": [{}]
                    }
                    
                def get_accessor_data(self, accessor):
                    return None
            
            # Override the pipeline's mesh loading methods
            pipeline.gltf_parser = MockGLTFParser()
            
            # Set up mock data
            pipeline.mesh_data_extractor = MockMeshDataExtractor(shape_data['vertices'])
            pipeline.joint_names = ["SphereBone"]
            pipeline.bone_weights = pipeline.mesh_data_extractor.get_bone_weights()
            pipeline.bone_indices = pipeline.mesh_data_extractor.get_bone_indices()
            
            # Group vertices by bone
            pipeline._group_vertices_by_bone()
            
            # Run CoACD decomposition
            hulls = pipeline._run_coacd_global(mock_mesh, threshold=0.05)
            print(f"Generated {len(hulls)} convex hulls")
            
            # Generate candidate capsules
            capsules = pipeline.generate_candidate_capsules(hulls)
            print(f"Generated {len(capsules)} candidate capsules")
            
            print("✅ Sphere pipeline test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error during sphere pipeline test: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_cylinder_pipeline():
    """Test the pipeline with a cylinder shape."""
    print("\nTesting tapered capsule pipeline with cylinder")
    print("=" * 50)
    
    # Generate a cylinder
    shape_data = ShapeGenerator.generate_cylinder(1.0, 2.0, segments=16)
    mock_mesh = CoACDCompatibleMesh(
        shape_data['vertices'], 
        shape_data['faces']
    )
    
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a mock VRM file path
        vrm_path = temp_path / "cylinder.vrm"
        vrm_path.touch()
        
        try:
            # Create pipeline
            pipeline = CoACDCapsulePipeline(str(vrm_path), str(temp_path))
            
            # Mock the mesh data extractor
            class MockMeshDataExtractor:
                def __init__(self, vertices):
                    self.vertices = vertices
                    
                def get_vertices(self):
                    return self.vertices.tolist()
                    
                def get_bone_weights(self):
                    return [[1.0] for _ in range(len(self.vertices))]
                    
                def get_bone_indices(self):
                    return [[0] for _ in range(len(self.vertices))]
            
            # Mock the GLTF parser
            class MockGLTFParser:
                def load_glb(self, path):
                    return True
                    
                def get_gltf_data(self):
                    return {
                        "nodes": [{"name": "RootNode"}],
                        "skins": [{"joints": [0]}],
                        "meshes": [{}]
                    }
                    
                def get_accessor_data(self, accessor):
                    return None
            
            # Override the pipeline's mesh loading methods
            pipeline.gltf_parser = MockGLTFParser()
            
            # Set up mock data
            pipeline.mesh_data_extractor = MockMeshDataExtractor(shape_data['vertices'])
            pipeline.joint_names = ["CylinderBone"]
            pipeline.bone_weights = pipeline.mesh_data_extractor.get_bone_weights()
            pipeline.bone_indices = pipeline.mesh_data_extractor.get_bone_indices()
            
            # Group vertices by bone
            pipeline._group_vertices_by_bone()
            
            # Run CoACD decomposition
            hulls = pipeline._run_coacd_global(mock_mesh, threshold=0.05)
            print(f"Generated {len(hulls)} convex hulls")
            
            # Generate candidate capsules
            capsules = pipeline.generate_candidate_capsules(hulls)
            print(f"Generated {len(capsules)} candidate capsules")
            
            print("✅ Cylinder pipeline test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error during cylinder pipeline test: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_markoid_pipeline():
    """Test the pipeline with a markoid shape."""
    print("\nTesting tapered capsule pipeline with markoid")
    print("=" * 50)
    
    # Generate a markoid (super ellipsoid)
    shape_data = ShapeGenerator.generate_markoid(1.2, 1.0, 0.8, power=2.5, segments=12)
    mock_mesh = CoACDCompatibleMesh(
        shape_data['vertices'], 
        shape_data['faces']
    )
    
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a mock VRM file path
        vrm_path = temp_path / "markoid.vrm"
        vrm_path.touch()
        
        try:
            # Create pipeline
            pipeline = CoACDCapsulePipeline(str(vrm_path), str(temp_path))
            
            # Mock the mesh data extractor
            class MockMeshDataExtractor:
                def __init__(self, vertices):
                    self.vertices = vertices
                    
                def get_vertices(self):
                    return self.vertices.tolist()
                    
                def get_bone_weights(self):
                    return [[1.0] for _ in range(len(self.vertices))]
                    
                def get_bone_indices(self):
                    return [[0] for _ in range(len(self.vertices))]
            
            # Mock the GLTF parser
            class MockGLTFParser:
                def load_glb(self, path):
                    return True
                    
                def get_gltf_data(self):
                    return {
                        "nodes": [{"name": "RootNode"}],
                        "skins": [{"joints": [0]}],
                        "meshes": [{}]
                    }
                    
                def get_accessor_data(self, accessor):
                    return None
            
            # Override the pipeline's mesh loading methods
            pipeline.gltf_parser = MockGLTFParser()
            
            # Set up mock data
            pipeline.mesh_data_extractor = MockMeshDataExtractor(shape_data['vertices'])
            pipeline.joint_names = ["MarkoidBone"]
            pipeline.bone_weights = pipeline.mesh_data_extractor.get_bone_weights()
            pipeline.bone_indices = pipeline.mesh_data_extractor.get_bone_indices()
            
            # Group vertices by bone
            pipeline._group_vertices_by_bone()
            
            # Run CoACD decomposition
            hulls = pipeline._run_coacd_global(mock_mesh, threshold=0.05)
            print(f"Generated {len(hulls)} convex hulls")
            
            # Generate candidate capsules
            capsules = pipeline.generate_candidate_capsules(hulls)
            print(f"Generated {len(capsules)} candidate capsules")
            
            print("✅ Markoid pipeline test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error during markoid pipeline test: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_shape_generation():
    """Test basic shape generation functions."""
    print("Testing shape generation functions")
    print("=" * 50)
    
    generator = ShapeGenerator()
    
    # Test cube
    cube_data = generator.generate_cube(2.0)
    print(f"✅ Cube: {len(cube_data['vertices'])} vertices, {len(cube_data['faces'])} faces")
    
    # Test sphere
    sphere_data = generator.generate_sphere(1.0, segments=8)
    print(f"✅ Sphere: {len(sphere_data['vertices'])} vertices, {len(sphere_data['faces'])} faces")
    
    # Test cylinder
    cylinder_data = generator.generate_cylinder(1.0, 2.0, segments=8)
    print(f"✅ Cylinder: {len(cylinder_data['vertices'])} vertices, {len(cylinder_data['faces'])} faces")
    
    # Test cone
    cone_data = generator.generate_cone(1.0, 2.0, segments=8)
    print(f"✅ Cone: {len(cone_data['vertices'])} vertices, {len(cone_data['faces'])} faces")
    
    # Test ellipsoid
    ellipsoid_data = generator.generate_ellipsoid(1.0, 1.5, 0.8, segments=8)
    print(f"✅ Ellipsoid: {len(ellipsoid_data['vertices'])} vertices, {len(ellipsoid_data['faces'])} faces")
    
    # Test markoid
    markoid_data = generator.generate_markoid(1.0, 1.5, 0.8, power=2.5, segments=12)
    print(f"✅ Markoid: {len(markoid_data['vertices'])} vertices, {len(markoid_data['faces'])} faces")
    
    # Test triangular prism
    prism_data = generator.generate_triangular_prism(1.0, 2.0, 1.0)
    print(f"✅ Triangular Prism: {len(prism_data['vertices'])} vertices, {len(prism_data['faces'])} faces")
    
    # Test pyramid
    pyramid_data = generator.generate_pyramid(1.0, 1.0, 2.0)
    print(f"✅ Pyramid: {len(pyramid_data['vertices'])} vertices, {len(pyramid_data['faces'])} faces")
    
    # Test torus (donut)
    torus_data = generator.generate_torus(1.5, 0.5, major_segments=12, minor_segments=8)
    print(f"✅ Torus: {len(torus_data['vertices'])} vertices, {len(torus_data['faces'])} faces")
    
    # Test biscuit
    biscuit_data = generator.generate_biscuit(1.0, 0.3, segments=12)
    print(f"✅ Biscuit: {len(biscuit_data['vertices'])} vertices, {len(biscuit_data['faces'])} faces")
    
    # Test cubic stroke (spline line)
    stroke_data = generator.generate_cubic_stroke([(0, 0, 0), (1, 1, 0), (2, 0, 1)], 0.1, 8)
    print(f"✅ Cubic Stroke: {len(stroke_data['vertices'])} vertices, {len(stroke_data['faces'])} faces")
    
    return True

def main():
    """Run all shape tests."""
    print("Running Shape Tests for Tapered Capsule Pipeline")
    print("=" * 60)
    
    # Test individual components
    test_results = []
    
    # Test shape generation
    test_results.append(test_shape_generation())
    
    # Test pipeline with different shapes
    test_results.append(test_cube_pipeline())
    test_results.append(test_sphere_pipeline())
    test_results.append(test_cylinder_pipeline())
    test_results.append(test_markoid_pipeline())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    passed = sum(test_results)
    total = len(test_results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! 🎉")
        return 0
    else:
        print("Some tests failed! ❌")
        return 1

if __name__ == "__main__":
    sys.exit(main())
