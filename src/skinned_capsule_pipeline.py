#!/usr/bin/env python3
"""
Skinned Capsule Pipeline with Robust Laplacian Weight Smoothing.
Complete pipeline from VRM analysis to skinned capsule glTF generation.
"""

import sys
import os
import json
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import argparse

# Import our modules
from .vrm_mesh_analyzer import VRMMeshAnalyzer
from .minizinc_to_gltf import GLTFCapsuleGenerator
from .capsule_skinning import CapsuleSkinningSystem

class SkinnedCapsulePipeline:
    """
    Complete pipeline for generating skinned capsule representations from VRM models.
    """
    
    def __init__(self):
        self.analyzer = VRMMeshAnalyzer()
        self.generator = GLTFCapsuleGenerator()
        self.skinning = CapsuleSkinningSystem()
        
        # Pipeline configuration
        self.config = {
            "max_capsules": 25,
            "scale_factor": 1000,
            "smoothing_iterations": 2,
            "vertex_color_mode": "bone_visualization",
            "enable_skinning": True,
            "enable_vertex_colors": True,
            "segments": 16  # Capsule mesh resolution
        }
    
    def load_vrm_and_analyze(self, vrm_path: str) -> bool:
        """Load VRM file and perform mesh analysis."""
        print(f"=== Loading and Analyzing VRM: {vrm_path} ===")
        
        if not self.analyzer.load_vrm_file(vrm_path):
            print(f"❌ Failed to load VRM file: {vrm_path}")
            return False
        
        self.analyzer.print_analysis_summary()
        return True
    
    def generate_optimization_data(self, output_path: str) -> bool:
        """Generate MiniZinc optimization data."""
        print(f"\n=== Generating Optimization Data ===")
        
        success = self.analyzer.save_cpsat_data(
            output_path, 
            self.config["max_capsules"], 
            self.config["scale_factor"]
        )
        
        if success:
            print(f"✅ Generated optimization data: {output_path}")
        else:
            print(f"❌ Failed to generate optimization data")
        
        return success
    
    def parse_optimization_results(self, results_path: str, dzn_path: str = None) -> List[Dict[str, Any]]:
        """Parse MiniZinc optimization results."""
        print(f"\n=== Parsing Optimization Results ===")
        
        try:
            with open(results_path, 'r') as f:
                results_content = f.read()
            
            capsules = self.generator.parse_minizinc_output(
                results_content, 
                manual_scale=self.config["scale_factor"],
                dzn_path=dzn_path
            )
            
            print(f"✅ Parsed {len(capsules)} capsules from results")
            return capsules
            
        except Exception as e:
            print(f"❌ Failed to parse optimization results: {e}")
            return []
    
    def generate_skinned_capsules(self, 
                                capsules: List[Dict[str, Any]], 
                                output_path: str,
                                vrm_path: str = None,
                                dzn_path: str = None) -> bool:
        """Generate skinned capsule glTF with weight transfer and vertex colors."""
        print(f"\n=== Generating Skinned Capsules ===")
        
        if not capsules:
            print("❌ No capsules to process")
            return False
        
        try:
            # Load VRM data for extensions if provided
            vrm_data = {}
            if vrm_path:
                vrm_data = self.generator.load_vrm_model(vrm_path)
            
            # Extract original mesh data for weight transfer
            original_mesh_data = self._extract_original_mesh_data()
            
            if not original_mesh_data:
                print("⚠️  No original mesh data available, generating capsules without skinning")
                return self._generate_basic_capsules(capsules, output_path, vrm_data, dzn_path)
            
            # Generate skinned capsules
            return self._generate_skinned_capsules_with_weights(
                capsules, output_path, original_mesh_data, vrm_data, dzn_path
            )
            
        except Exception as e:
            print(f"❌ Failed to generate skinned capsules: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_original_mesh_data(self) -> Optional[Dict[str, Any]]:
        """Extract original mesh data from the analyzer for weight transfer."""
        if not self.analyzer.vertices or not self.analyzer.bone_weights:
            return None
        
        # Convert triangle indices to face format
        faces = []
        for i in range(0, len(self.analyzer.triangles), 3):
            if i + 2 < len(self.analyzer.triangles):
                faces.append([
                    self.analyzer.triangles[i],
                    self.analyzer.triangles[i + 1], 
                    self.analyzer.triangles[i + 2]
                ])
        
        return {
            'vertices': self.analyzer.vertices,
            'faces': faces,
            'bone_weights': self.analyzer.bone_weights,
            'bone_indices': self.analyzer.bone_indices,
            'joint_names': self.analyzer.joint_names
        }
    
    def _generate_basic_capsules(self, 
                               capsules: List[Dict[str, Any]], 
                               output_path: str,
                               vrm_data: Dict[str, Any],
                               dzn_path: str = None) -> bool:
        """Generate basic capsules without skinning."""
        print("Generating basic capsules without skinning data...")
        
        # Generate capsule meshes
        for i, capsule in enumerate(capsules):
            position = capsule['position']
            length = capsule['length']
            r1 = capsule['radius1']
            r2 = capsule['radius2']
            rotation_matrix = capsule.get('rotation_matrix')
            bone_name = capsule.get('bone_name', f"Bone_{i}")
            
            # Generate capsule mesh
            capsule_mesh = self.generator.generate_capsule_mesh(
                length, r1, r2, segments=self.config["segments"]
            )
            
            # Add to scene
            self.generator.add_capsule_to_scene(
                capsule_mesh, 
                i + 1, 
                position=position,
                rotation_matrix=rotation_matrix,
                bone_name=bone_name
            )
        
        # Generate final glTF
        gltf_data = self.generator.generate_gltf(capsules, vrm_data, dzn_path)
        self.generator.save_gltf(output_path)
        
        print(f"✅ Generated basic capsule glTF: {output_path}")
        return True
    
    def _generate_skinned_capsules_with_weights(self,
                                              capsules: List[Dict[str, Any]], 
                                              output_path: str,
                                              original_mesh_data: Dict[str, Any],
                                              vrm_data: Dict[str, Any],
                                              dzn_path: str = None) -> bool:
        """Generate capsules with full skinning and vertex color support."""
        print("Generating skinned capsules with weight transfer and vertex colors...")
        
        # Generate capsule meshes with skinning
        for i, capsule in enumerate(capsules):
            position = capsule['position']
            length = capsule['length']
            r1 = capsule['radius1']
            r2 = capsule['radius2']
            rotation_matrix = capsule.get('rotation_matrix')
            bone_name = capsule.get('bone_name', f"Bone_{i}")
            
            print(f"\nProcessing capsule {i+1}/{len(capsules)}: {bone_name}")
            
            # Generate capsule mesh
            capsule_mesh = self.generator.generate_capsule_mesh(
                length, r1, r2, segments=self.config["segments"]
            )
            
            # Convert mesh data to numpy arrays
            capsule_vertices = np.array(capsule_mesh['vertices']).reshape(-1, 3)
            capsule_faces = np.array(capsule_mesh['indices']).reshape(-1, 3)
            
            skinning_data = None
            vertex_colors = None
            
            # Generate skinning data if enabled
            if self.config["enable_skinning"]:
                try:
                    # Transfer and smooth weights
                    smooth_weights, bone_indices = self.skinning.transfer_and_smooth_capsule_weights(
                        capsule_vertices,
                        capsule_faces,
                        original_mesh_data,
                        smoothing_iterations=self.config["smoothing_iterations"]
                    )
                    
                    # Prepare skinning data for glTF
                    joints_data, weights_data = self.skinning.prepare_skinning_data(
                        smooth_weights, bone_indices
                    )
                    
                    skinning_data = {
                        "joints": joints_data,
                        "weights": weights_data
                    }
                    
                    print(f"  ✅ Generated skinning data: {len(joints_data)} vertices")
                    
                    # Generate vertex colors if enabled
                    if self.config["enable_vertex_colors"]:
                        vertex_colors = self.skinning.generate_vertex_colors(
                            smooth_weights, 
                            bone_indices, 
                            mode=self.config["vertex_color_mode"],
                            bone_names=original_mesh_data.get('joint_names')
                        )
                        print(f"  ✅ Generated vertex colors: {self.config['vertex_color_mode']} mode")
                    
                except Exception as e:
                    print(f"  ⚠️  Skinning failed for capsule {i+1}: {e}")
                    print("  Falling back to basic capsule generation")
            
            # Add capsule to scene
            self.generator.add_capsule_to_scene(
                capsule_mesh, 
                i + 1, 
                position=position,
                rotation_matrix=rotation_matrix,
                bone_name=bone_name,
                skinning_data=skinning_data,
                vertex_colors=vertex_colors
            )
        
        # Generate final glTF
        gltf_data = self.generator.generate_gltf(capsules, vrm_data, dzn_path)
        self.generator.save_gltf(output_path)
        
        print(f"\n✅ Generated skinned capsule glTF: {output_path}")
        
        # Print statistics
        total_vertices = sum(
            gltf_data["accessors"][mesh["primitives"][0]["attributes"]["POSITION"]]["count"] 
            for mesh in gltf_data["meshes"] if "primitives" in mesh
        )
        print(f"📊 Statistics:")
        print(f"   Total capsules: {len(capsules)}")
        print(f"   Total vertices: {total_vertices}")
        print(f"   Total meshes: {len(gltf_data['meshes'])}")
        
        return True
    
    def run_full_pipeline(self, 
                         vrm_path: str,
                         results_path: str,
                         output_path: str,
                         dzn_path: str = None) -> bool:
        """Run the complete pipeline from VRM to skinned capsules."""
        print(f"🚀 Starting Skinned Capsule Pipeline")
        print(f"   VRM Input: {vrm_path}")
        print(f"   Results Input: {results_path}")
        print(f"   glTF Output: {output_path}")
        print(f"   DZN Data: {dzn_path or 'Auto-detect'}")
        
        # Step 1: Load and analyze VRM
        if not self.load_vrm_and_analyze(vrm_path):
            return False
        
        # Step 2: Parse optimization results
        capsules = self.parse_optimization_results(results_path, dzn_path)
        if not capsules:
            return False
        
        # Step 3: Generate skinned capsules
        success = self.generate_skinned_capsules(
            capsules, output_path, vrm_path, dzn_path
        )
        
        if success:
            print(f"\n🎉 Pipeline completed successfully!")
            print(f"   Output: {output_path}")
        else:
            print(f"\n❌ Pipeline failed")
        
        return success
    
    def configure(self, **kwargs):
        """Update pipeline configuration."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                print(f"Updated config: {key} = {value}")
            else:
                print(f"Warning: Unknown config key: {key}")

def main():
    parser = argparse.ArgumentParser(
        description='Skinned Capsule Pipeline with Robust Laplacian Weight Smoothing'
    )
    
    parser.add_argument('vrm_file', help='Input VRM file path')
    parser.add_argument('results_file', help='MiniZinc optimization results file')
    parser.add_argument('output_file', help='Output skinned glTF file path')
    
    parser.add_argument('--dzn', help='DZN data file path (auto-detect if not provided)')
    parser.add_argument('--max-capsules', type=int, default=25, help='Maximum number of capsules')
    parser.add_argument('--scale', type=int, default=1000, help='Integer scaling factor')
    parser.add_argument('--smoothing-iterations', type=int, default=2, help='Weight smoothing iterations')
    parser.add_argument('--color-mode', default='bone_visualization', 
                       choices=['bone_visualization', 'weight_strength', 'dominant_bone_strength', 'bone_count'],
                       help='Vertex color visualization mode')
    parser.add_argument('--segments', type=int, default=16, help='Capsule mesh segments')
    parser.add_argument('--no-skinning', action='store_true', help='Disable skinning (basic capsules only)')
    parser.add_argument('--no-colors', action='store_true', help='Disable vertex colors')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.vrm_file):
        print(f"❌ VRM file not found: {args.vrm_file}")
        sys.exit(1)
    
    if not os.path.exists(args.results_file):
        print(f"❌ Results file not found: {args.results_file}")
        sys.exit(1)
    
    # Auto-detect DZN file if not provided
    dzn_path = args.dzn
    if not dzn_path:
        # Try common locations
        candidates = [
            "analysis_cpsat.dzn",
            "../analysis_cpsat.dzn",
            os.path.join(os.path.dirname(args.vrm_file), "analysis_cpsat.dzn")
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                dzn_path = candidate
                print(f"Auto-detected DZN file: {dzn_path}")
                break
    
    # Create and configure pipeline
    pipeline = SkinnedCapsulePipeline()
    
    pipeline.configure(
        max_capsules=args.max_capsules,
        scale_factor=args.scale,
        smoothing_iterations=args.smoothing_iterations,
        vertex_color_mode=args.color_mode,
        enable_skinning=not args.no_skinning,
        enable_vertex_colors=not args.no_colors,
        segments=args.segments
    )
    
    # Run pipeline
    try:
        success = pipeline.run_full_pipeline(
            args.vrm_file,
            args.results_file, 
            args.output_file,
            dzn_path
        )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
