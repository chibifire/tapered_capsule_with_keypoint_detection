#!/usr/bin/env python3
"""
VRM1 Mesh Analyzer for Tapered Capsule Generation.
Analyzes skinned meshes in VRM1 files to generate optimal tapered capsule representations.
"""

from typing import Dict, Any, Optional
from gltf_parser import GLTFParser
from skeleton_analyzer import SkeletonAnalyzer
from mesh_data_extractor import MeshDataExtractor
from capsule_generator import CapsuleGenerator

class VRMMeshAnalyzer:
    """Analyzes VRM mesh geometry and extracts bone-related data."""
    
    def __init__(self):
        self.gltf_parser = GLTFParser()
        self.skeleton_analyzer: Optional[SkeletonAnalyzer] = None
        self.mesh_data_extractor: Optional[MeshDataExtractor] = None
        self.capsule_generator: Optional[CapsuleGenerator] = None
        self.vrm_path: Optional[str] = None
        self.bone_analysis_data: Optional[Dict[str, Any]] = None
        
    def load_vrm_file(self, vrm_path: str) -> bool:
        """Load VRM file and perform mesh analysis."""
        self.vrm_path = vrm_path
        if not self.gltf_parser.load_glb(vrm_path):
            print(f"Error: Failed to load and analyze VRM file: {vrm_path}")
            return False
        
        gltf_data = self.gltf_parser.get_gltf_data()
        
        self.skeleton_analyzer = SkeletonAnalyzer(gltf_data)
        self.skeleton_analyzer.extract_skeleton()
        
        self.mesh_data_extractor = MeshDataExtractor(gltf_data, self.gltf_parser.get_accessor_data)
        self.mesh_data_extractor.extract_mesh_data()
        
        self.capsule_generator = CapsuleGenerator(
            self.skeleton_analyzer.get_joint_names(),
            self.skeleton_analyzer.get_bone_positions(),
            self.skeleton_analyzer.get_bone_rotations(),
            self.skeleton_analyzer.get_bone_directions(),
            self.skeleton_analyzer.get_vrm_humanoid_bones()
        )
        
        self.bone_analysis_data = self.capsule_generator.analyze_bone_geometry(
            self.mesh_data_extractor.get_vertices(),
            self.mesh_data_extractor.get_bone_weights(),
            self.mesh_data_extractor.get_bone_indices()
        )
        
        return True

    def generate_capsule_constraints(self, max_capsules: int = 25, integer_scale: int = None, fast_mode: bool = False) -> str:
        if not self.capsule_generator or not self.bone_analysis_data:
            return ""
        return self.capsule_generator.generate_capsule_constraints(self.bone_analysis_data, max_capsules, integer_scale, fast_mode)

    def save_analysis_data(self, output_path: str, integer_scale: int = None):
        """Save analysis data to DZN file for MiniZinc."""
        if not self.capsule_generator or not self.bone_analysis_data:
            print("No data to save")
            return False
        
        constraints = self.capsule_generator.generate_capsule_constraints(self.bone_analysis_data, integer_scale=integer_scale)
        
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
        """Save float data for Gecode solver."""
        if not self.capsule_generator or not self.bone_analysis_data:
            print("No data to save")
            return False
            
        constraints = self.capsule_generator.generate_capsule_constraints(self.bone_analysis_data, max_capsules=max_capsules)
        
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
        """Parse CP-SAT results and export to JSON format."""
        if not self.capsule_generator:
            return False
        return self.capsule_generator.export_cpsat_results_to_json(results_file, output_file, scale)

    def export_cpsat_results_to_csv(self, results_file: str, output_file: str, scale: int = 1000):
        """Parse CP-SAT results and export to CSV format."""
        if not self.capsule_generator:
            return False
        return self.capsule_generator.export_cpsat_results_to_csv(results_file, output_file, scale)

    def print_analysis_summary(self):
        """Print summary of the mesh analysis."""
        if not self.mesh_data_extractor or not self.skeleton_analyzer or not self.bone_analysis_data:
            return

        print(f"\nVRM Mesh Analysis Summary:")
        print(f"Total vertices: {len(self.mesh_data_extractor.get_vertices())}")
        print(f"Total triangles: {len(self.mesh_data_extractor.get_triangles())}")
        print(f"Total normals: {len(self.mesh_data_extractor.get_normals())}")
        print(f"Total joints: {len(self.skeleton_analyzer.get_joint_names())}")
        print(f"Meshes analyzed: {len(self.mesh_data_extractor.get_mesh_bounds())}")
        
        # Show triangle mesh data per mesh
        total_surface_area = 0.0
        print(f"\nTriangle Mesh Data:")
        for mesh_name, bounds in self.mesh_data_extractor.get_mesh_bounds().items():
            surface_area = bounds.get('surface_area', 0.0)
            total_surface_area += surface_area
            print(f"  {mesh_name}: {bounds['vertex_count']} vertices, "
                  f"{bounds['triangle_count']} triangles, "
                  f"surface_area={surface_area:.6f}")
        
        print(f"Total surface area: {total_surface_area:.6f}")
        
        print(f"\nBone geometry analysis (with triangle mesh support):")
        
        # Sort by vertex count
        sorted_bones = sorted(
            self.bone_analysis_data.items(),
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

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("VRM Capsule Optimizer - Gecode Float Solver")
        print("Usage: python vrm_mesh_analyzer.py <vrm_file.gltf> [options]")
        print("  vrm_file.gltf: Input VRM1 GLTF file")
        print("  --output <file>: Output base name (default: vrm_analysis)")
        print("  --capsules <n>: Maximum number of capsules (default: 25)")
        print("  --export-json: Export results to JSON format")
        print("  --export-csv: Export results to CSV format")
        print("  --results <file>: Gecode results file to process")
        sys.exit(1)
    
    # Parse command line arguments
    vrm_file = sys.argv[1]
    output_base = "vrm_analysis"
    max_capsules = 25
    export_json = False
    export_csv = False
    results_file = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_base = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--capsules" and i + 1 < len(sys.argv):
            max_capsules = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--export-json":
            export_json = True
            i += 1
        elif sys.argv[i] == "--export-csv":
            export_csv = True
            i += 1
        elif sys.argv[i] == "--results" and i + 1 < len(sys.argv):
            results_file = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    try:
        analyzer = VRMMeshAnalyzer()
        
        print(f"=== VRM Capsule Optimizer - Gecode Float Solver ===")
        print(f"Loading VRM file: {vrm_file}")
        if not analyzer.load_vrm_file(vrm_file):
            print("Failed to load VRM file")
            sys.exit(1)
        
        analyzer.print_analysis_summary()
        
        # Generate Gecode float data (primary output)
        gecode_file = f"{output_base}_gecode.dzn"
        if analyzer.save_gecode_data(gecode_file, max_capsules):
            print(f"\n✅ Generated Gecode float data: {gecode_file}")
            print(f"   Using float values (no scaling)")
        
        # Generate float data for comparison (optional)
        float_file = f"{output_base}_float.dzn"
        if analyzer.save_analysis_data(float_file):
            print(f"✅ Generated float data (for comparison): {float_file}")
        
        print(f"\n=== Gecode Optimization Workflow ===")
        print(f"1. Run Gecode solver:")
        print(f"   minizinc --solver gecode --parallel 16 tapered_capsule.mzn {gecode_file} -o results_gecode.txt")
        print(f"2. Export results (optional):")
        print(f"   python vrm_mesh_analyzer.py {vrm_file} --results results_gecode.txt --export-json --export-csv")
        
        # Process results if provided
        if results_file:
            print(f"\n=== Processing Gecode Results ===")
            if export_json:
                json_file = f"{output_base}_results.json"
                if analyzer.export_cpsat_results_to_json(results_file, json_file):
                    print(f"✅ Exported to JSON: {json_file}")
            
            if export_csv:
                csv_file = f"{output_base}_results.csv"
                if analyzer.export_cpsat_results_to_csv(results_file, csv_file):
                    print(f"✅ Exported to CSV: {csv_file}")
        
        print(f"\n=== Optimization Complete ===")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
