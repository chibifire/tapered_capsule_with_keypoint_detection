#!/usr/bin/env python3
"""
Complete VRM to Tapered Capsules Pipeline.
Analyzes VRM mesh, runs constraint optimization with witness point coverage, and generates GLTF output.
"""

import os
import sys
import subprocess
import tempfile
import numpy as np
from pathlib import Path
from .vrm_mesh_analyzer import VRMMeshAnalyzer

class VRMCapsulePipeline:
    def __init__(self, vrm_path: str, output_dir: str = None):
        self.temp_files = []
        self.output_dir = Path(output_dir) if output_dir else Path(vrm_path).parent
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.original_vrm_path = Path(vrm_path)
        self.output_dir = Path(output_dir) if output_dir else self.original_vrm_path.parent
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.vrm_path = self.output_dir / f"{self.original_vrm_path.stem}_duplicate{self.original_vrm_path.suffix}"
        with open(self.original_vrm_path, 'rb') as src, open(self.vrm_path, 'wb') as dst:
            dst.write(src.read())
        self.temp_files = []
        self.output_dir = Path(output_dir) if output_dir else self.vrm_path.parent
        self.temp_files = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize mesh data
        self.vertices = None
        self.triangles = None
        self.bone_weights = None
        self.bone_indices = None
        self.joint_names = []
        
    def __del__(self):
        """Clean up temporary files."""
        if hasattr(self, 'temp_files'):
            for temp_file in self.temp_files:
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                except:
                    pass
    
    def analyze_vrm_mesh(self, max_capsules: int = 8) -> bool:
        """Step 1: Analyze VRM mesh and generate constraint data."""
        print(f"Step 1: Analyzing VRM mesh: {self.vrm_path}")
        
        # Create analyzer
        analyzer = VRMMeshAnalyzer()
        
        # Load VRM file
        if not analyzer.load_vrm_file(str(self.vrm_path)):
            print("Failed to load VRM file")
            return False
        
        # Print analysis summary
        analyzer.print_analysis_summary()
        
        # Store mesh data for witness point sampling
        self.vertices = analyzer.mesh_data_extractor.get_vertices()
        self.triangles = analyzer.mesh_data_extractor.get_triangles()
        self.bone_weights = analyzer.mesh_data_extractor.get_bone_weights()
        self.bone_indices = analyzer.mesh_data_extractor.get_bone_indices()
        self.joint_names = analyzer.skeleton_analyzer.get_joint_names()
        
        # Generate constraint data for Gecode (float values)
        self.constraints_file = self.output_dir / f"{self.vrm_path.stem}_constraints.dzn"
        if not analyzer.save_gecode_data(str(self.constraints_file), max_capsules):
            print("Failed to generate constraint data")
            return False
        
        # Also generate float data for float solvers
        self.float_constraints_file = self.output_dir / f"{self.vrm_path.stem}_float.dzn"
        if not analyzer.save_analysis_data(str(self.float_constraints_file)):
            print("Failed to generate float constraint data")
            return False
        
        self.temp_files.append(self.constraints_file)
        self.temp_files.append(self.float_constraints_file)
        print(f"Generated constraint data: {self.constraints_file}")
        print(f"Generated float data: {self.float_constraints_file}")
        return True
    
    def sample_witness_points(self, num_points: int = 5000) -> np.ndarray:
        """Sample witness points from mesh interior for coverage verification."""
        print(f"Step 1b: Sampling {num_points} witness points from mesh")
        
        if self.vertices is None or len(self.vertices) == 0:
            print("  ❌ No vertex data available for sampling")
            return None
        
        try:
            # Convert to numpy array
            vertices = np.array(self.vertices)
            
            # Calculate mesh bounds
            min_bounds = np.min(vertices, axis=0)
            max_bounds = np.max(vertices, axis=0)
            
            # Sample points within mesh bounds
            # In a more sophisticated implementation, we'd sample within the actual mesh volume
            # For now, we'll sample uniformly within the bounding box
            witness_points = np.random.uniform(min_bounds, max_bounds, (num_points, 3))
            
            print(f"  ✅ Sampled {len(witness_points)} witness points")
            return witness_points
            
        except Exception as e:
            print(f"  ❌ Error sampling witness points: {e}")
            return None
    
    def build_coverage_matrix(self, witness_points: np.ndarray) -> np.ndarray:
        """Build coverage matrix using bone geometry data."""
        print("Step 1c: Building coverage matrix from bone geometry")
        
        if witness_points is None or len(witness_points) == 0:
            print("  ❌ No witness points available")
            return None
        
        # Load the constraint data to get bone information
        if not hasattr(self, 'constraints_file') or not self.constraints_file.exists():
            print("  ❌ No constraint data available")
            return None
        
        try:
            # Parse the constraint file to get bone data
            with open(self.constraints_file, 'r') as f:
                constraint_data = f.read()
            
            # Extract bone information from constraint data
            import re
            
            # Extract n_capsules
            n_capsules_match = re.search(r'n_capsules = (\d+);', constraint_data)
            if not n_capsules_match:
                print("  ❌ Could not find n_capsules in constraint data")
                return None
            n_capsules = int(n_capsules_match.group(1))
            
            # Extract bone_centers
            bone_centers_match = re.search(r'bone_centers = array2d\(1\.\.(\d+), 1\.\.3, \[([^\]]+)\]\);', constraint_data)
            if not bone_centers_match:
                print("  ❌ Could not find bone_centers in constraint data")
                return None
            
            centers_str = bone_centers_match.group(2)
            center_values = [float(x.strip()) for x in centers_str.split(',')]
            bone_centers = np.array(center_values).reshape(n_capsules, 3)
            
            # Extract bone_sizes
            bone_sizes_match = re.search(r'bone_sizes = array2d\(1\.\.(\d+), 1\.\.3, \[([^\]]+)\]\);', constraint_data)
            if not bone_sizes_match:
                print("  ❌ Could not find bone_sizes in constraint data")
                return None
            
            sizes_str = bone_sizes_match.group(2)
            size_values = [float(x.strip()) for x in sizes_str.split(',')]
            bone_sizes = np.array(size_values).reshape(n_capsules, 3)
            
            print(f"  Found {n_capsules} bones for coverage matrix")
            
            # Initialize coverage matrix
            num_points = len(witness_points)
            coverage_matrix = np.zeros((n_capsules, num_points), dtype=bool)
            
            # For each witness point, check which bones it's close to
            for i, point in enumerate(witness_points):
                for j in range(n_capsules):
                    # Check if point is within the bone's bounding box
                    center = bone_centers[j]
                    size = bone_sizes[j]
                    
                    # Calculate bounds for this bone
                    min_bound = center - size / 2
                    max_bound = center + size / 2
                    
                    # Check if point is within bounds
                    if np.all(point >= min_bound) and np.all(point <= max_bound):
                        coverage_matrix[j, i] = True
            
            print(f"  ✅ Built {n_capsules}x{num_points} coverage matrix")
            print(f"     Total covered points: {np.sum(np.any(coverage_matrix, axis=0))}/{num_points}")
            
            return coverage_matrix
            
        except Exception as e:
            print(f"  ❌ Error building coverage matrix: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_enhanced_constraint_data(self, witness_points: np.ndarray, coverage_matrix: np.ndarray) -> bool:
        """Create enhanced constraint data with witness point coverage."""
        print("Step 1d: Creating enhanced constraint data with coverage matrix")
        
        if witness_points is None or coverage_matrix is None:
            print("  ❌ No witness point data or coverage matrix available")
            return False
        
        try:
            # Read the original constraint data
            with open(self.constraints_file, 'r') as f:
                original_data = f.read()
            
            # Remove any existing witness point data from the original data
            import re
            # Remove existing witness point section (everything from the comment to the end)
            # This is a more robust approach - remove everything from the witness point comment onwards
            lines = original_data.split('\n')
            witness_section_start = -1
            for i, line in enumerate(lines):
                if '% Witness point coverage data' in line:
                    witness_section_start = i
                    break
            
            if witness_section_start >= 0:
                # Remove the witness point section
                lines = lines[:witness_section_start]
                original_data = '\n'.join(lines)
            
            # Append coverage matrix data to the constraint file
            enhanced_data = original_data.rstrip() + "\n\n"
            enhanced_data += "% Witness point coverage data\n"
            enhanced_data += f"num_points = {len(witness_points)};\n"
            
            # Add witness points
            points_list = []
            for point in witness_points:
                points_list.append(f"[{point[0]:.6f}, {point[1]:.6f}, {point[2]:.6f}]")
            enhanced_data += f"witness_points = array2d(1..{len(witness_points)}, 1..3, [{', '.join(points_list)}]);\n"
            
            # Add coverage matrix (as a flattened array)
            coverage_flat = coverage_matrix.flatten().astype(int).tolist()
            enhanced_data += f"coverage_matrix = array2d(1..{coverage_matrix.shape[0]}, 1..{coverage_matrix.shape[1]}, [{', '.join(map(str, coverage_flat))}]);\n"
            
            # Save enhanced constraint data
            self.enhanced_constraints_file = self.output_dir / f"{self.vrm_path.stem}_enhanced_constraints.dzn"
            with open(self.enhanced_constraints_file, 'w') as f:
                f.write(enhanced_data)
            
            print(f"  ✅ Created enhanced constraint data: {self.enhanced_constraints_file}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error creating enhanced constraint data: {e}")
            return False
    
    def run_single_optimization(self, capsule_count: int, timeout: int = 300, solver: str = "gecode") -> tuple[bool, str]:
        """Run a single optimization attempt with specified parameters."""
        
        # Determine which constraint file to use
        # Prefer enhanced constraint data with coverage if available
        if hasattr(self, 'enhanced_constraints_file') and self.enhanced_constraints_file.exists():
            base_constraints_file = self.enhanced_constraints_file
            print(f"  Using enhanced constraint data with coverage: {base_constraints_file.name}")
        else:
            base_constraints_file = self.constraints_file
            print(f"  Using basic constraint data: {base_constraints_file.name}")
        
        # Generate constraint file for specific capsule count
        analyzer = VRMMeshAnalyzer()
        if not analyzer.load_vrm_file(str(self.vrm_path)):
            return False, "Failed to reload VRM file"
        
        temp_constraints_file = self.output_dir / f"{self.vrm_path.stem}_temp_{capsule_count}caps.dzn"
        
        # If using enhanced data, we need to modify it for the specific capsule count
        if base_constraints_file == self.enhanced_constraints_file:
            # Read the enhanced constraint data
            with open(base_constraints_file, 'r') as f:
                enhanced_data = f.read()
            
            # Extract the n_capsules line and replace it with the specific count
            import re
            enhanced_data = re.sub(r'n_capsules = \d+;', f'n_capsules = {capsule_count};', enhanced_data)
            
            # Save the modified data
            with open(temp_constraints_file, 'w') as f:
                f.write(enhanced_data)
        else:
            # Generate new constraint data for the specific capsule count
            if not analyzer.save_gecode_data(str(temp_constraints_file), capsule_count):
                return False, f"Failed to generate constraint data for {capsule_count} capsules"
        
        model_file = Path(__file__).parent / "tapered_capsule.mzn"
        if not model_file.exists():
            return False, f"MiniZinc model not found: {model_file}"
        
        # Output file for results
        temp_results_file = self.output_dir / f"{self.vrm_path.stem}_temp_{capsule_count}caps_results.txt"
        
        # Run MiniZinc with specified solver
        cmd = [
            "minizinc",
            "--solver", solver,
            "--time-limit", str(timeout * 1000),  # MiniZinc expects milliseconds
            str(model_file),
            str(temp_constraints_file)
        ]
        
        try:
            print(f"  Trying {capsule_count} capsules with {solver} solver (timeout: {timeout}s)")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
            
            if result.returncode != 0:
                error_msg = f"Solver failed with return code {result.returncode}: {result.stderr}"
                return False, error_msg
            
            # Check if we got a valid solution
            if "==========\n" in result.stdout or "Capsule" in result.stdout:
                # Save successful results
                with open(temp_results_file, 'w') as f:
                    f.write(result.stdout)
                
                # Copy to main results file
                self.results_file = self.output_dir / f"{self.vrm_path.stem}_results.txt"
                with open(self.results_file, 'w') as f:
                    f.write(result.stdout)
                
                print(f"  ✅ Success! Found solution with {capsule_count} capsules")
                return True, f"Success with {capsule_count} capsules"
            else:
                return False, "No valid solution found in output"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout after {timeout} seconds"
        except FileNotFoundError:
            return False, "MiniZinc not found. Please install MiniZinc and ensure it's in your PATH."
        except Exception as e:
            return False, f"Unexpected error: {e}"
        finally:
            # Clean up temporary files
            try:
                if temp_constraints_file.exists():
                    temp_constraints_file.unlink()
                if temp_results_file.exists() and temp_results_file != self.results_file:
                    temp_results_file.unlink()
            except:
                pass

    def run_optimization(self, max_capsules: int = 25, timeout: int = 30) -> bool:
        """Step 2: Run MiniZinc constraint optimization with progressive approach."""
        
        if not hasattr(self, 'constraints_file'):
            print("No constraint data available. Run analyze_vrm_mesh first.")
            return False
        
        print(f"Step 2: Running progressive optimization (up to {max_capsules} capsules)")
        
        # Define optimization strategy
        solvers = ["gecode"]  # Always use Gecode solver only
        
        # Progressive capsule counts - start small and increase
        if max_capsules <= 5:
            capsule_counts = [max_capsules]
        elif max_capsules <= 10:
            capsule_counts = [3, 5, max_capsules]
        elif max_capsules <= 25:
            capsule_counts = [3, 5, 8, 12, max_capsules]
        else:
            capsule_counts = [3, 5, 8, 12, 20, 30, max_capsules]
        
        # Progressive timeouts - more time for larger problems
        def get_timeout(capsule_count):
            if capsule_count <= 5:
                return min(timeout, 15)
            elif capsule_count <= 10:
                return min(timeout, 30)
            elif capsule_count <= 20:
                return min(timeout, 60)
            else:
                return timeout
        
        best_result = None
        best_capsule_count = 0
        
        print(f"Trying capsule counts: {capsule_counts}")
        
        for capsule_count in capsule_counts:
            print(f"\n--- Attempting {capsule_count} capsules ---")
            
            # Try different solvers for this capsule count
            for solver in solvers:
                current_timeout = get_timeout(capsule_count)
                success, message = self.run_single_optimization(capsule_count, current_timeout, solver)
                
                if success:
                    best_result = message
                    best_capsule_count = capsule_count
                    print(f"  ✅ {message}")
                    break  # Success with this capsule count, try next count
                else:
                    print(f"  ❌ {solver}: {message}")
            
            # If we failed with all solvers for this capsule count, stop trying larger counts
            if not success:
                print(f"  ⚠️  Failed to solve with {capsule_count} capsules using all available solvers")
                if best_result:
                    print(f"  📝 Stopping here. Best result so far: {best_result}")
                    break
                else:
                    # Try with even fewer capsules if we haven't found any solution yet
                    if capsule_count > 1:
                        print(f"  🔄 Trying with just 1 capsule as fallback...")
                        success, message = self.run_single_optimization(1, 15, "gecode")
                        if success:
                            best_result = message
                            best_capsule_count = 1
                            break
        
        if best_result:
            print(f"\n🎉 Optimization completed successfully!")
            print(f"   Best result: {best_result}")
            print(f"   Results saved to: {self.results_file}")
            return True
        else:
            print(f"\n❌ Optimization failed completely")
            print(f"   Unable to find a solution with any capsule count or solver")
            print(f"   Try reducing the problem complexity or checking the input VRM file")
            return False
    
    
    def generate_gltf_model(self) -> bool:
        """Step 3 (alternative): Generate GLTF model from optimization results."""
        print("Step 3: Generating GLTF model")
        
        if not hasattr(self, 'results_file'):
            print("No optimization results available. Run run_optimization first.")
            return False
        
        # Import here to avoid circular imports
        from .minizinc_to_gltf import GLTFCapsuleGenerator
        
        # Output GLTF file
        self.gltf_file = self.output_dir / f"{self.vrm_path.stem}_capsules.gltf"
        
        try:
            # Create GLTF generator
            generator = GLTFCapsuleGenerator()
            
            # Read optimization results
            with open(self.results_file, 'r') as f:
                minizinc_output = f.read()
            
            # Parse capsule data
            capsules = generator.parse_minizinc_output(minizinc_output)
            
            if not capsules:
                print("No capsules found in optimization results!")
                return False
            
            print(f"Found {len(capsules)} optimized capsules")
            
            # Load original VRM for extensions
            vrm_data = generator.load_vrm_model(str(self.vrm_path))
            
            # Generate GLTF with flat structure (no hierarchy)
            generator.generate_gltf(capsules, vrm_data)  # Use vrm_data to place capsules on a copy of the original VRM
            generator.save_gltf(str(self.gltf_file))
            
            print(f"Generated GLTF model: {self.gltf_file}")
            return True
            
        except Exception as e:
            print(f"Error generating GLTF model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_complete_pipeline(self, max_capsules: int = 8, timeout: int = 30) -> bool:
        """Run the complete pipeline from VRM to optimized capsules (GLTF output only)."""
        print(f"Starting VRM to Capsules Pipeline for: {self.vrm_path}")
        print(f"Output directory: {self.output_dir}")
        print(f"Max capsules: {max_capsules}")
        print(f"Output format: GLTF")
        print("-" * 60)
        
        # Step 1: Analyze VRM mesh
        if not self.analyze_vrm_mesh(max_capsules):
            print("Pipeline failed at mesh analysis step")
            return False
        
        print("-" * 60)
        
        # Step 1b: Sample witness points for coverage
        witness_points = self.sample_witness_points(5000)
        if witness_points is None:
            print("Warning: Failed to sample witness points, continuing with basic optimization")
        else:
            print("-" * 60)
            
            # Step 1c: Build coverage matrix
            coverage_matrix = self.build_coverage_matrix(witness_points)
            if coverage_matrix is None:
                print("Warning: Failed to build coverage matrix, continuing with basic optimization")
            else:
                print("-" * 60)
                
                # Step 1d: Create enhanced constraint data with coverage
                if self.create_enhanced_constraint_data(witness_points, coverage_matrix):
                    print("✅ Enhanced constraint data with coverage matrix created successfully")
                else:
                    print("Warning: Failed to create enhanced constraint data, continuing with basic optimization")
        
        print("-" * 60)
        
        # Step 2: Run optimization
        if not self.run_optimization(max_capsules, timeout):
            print("Pipeline failed at optimization step")
            return False
        
        print("-" * 60)
        
        # Step 3: Generate GLTF model
        if not self.generate_gltf_model():
            print("Failed to generate GLTF model")
            return False
        
        print("-" * 60)
        print("Pipeline completed successfully!")
        print(f"Output files in: {self.output_dir}")
        
        if hasattr(self, 'gltf_file') and self.gltf_file.exists():
            print(f"  GLTF model: {self.gltf_file}")
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert VRM avatars to optimized tapered capsule representations"
    )
    parser.add_argument("vrm_file", help="Input VRM1 GLTF file")
    parser.add_argument("-o", "--output-dir", help="Output directory (default: same as input)")
    parser.add_argument("-n", "--max-capsules", type=int, default=25, 
                       help="Maximum number of capsules (default: 25)")
    parser.add_argument("-f", "--format", choices=["gltf"], default="gltf",
                       help="Output format (GLTF only)")
    parser.add_argument("-t", "--timeout", type=int, default=30,
                       help="Optimization timeout in seconds (default: 30)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Validate input file
    vrm_path = Path(args.vrm_file)
    if not vrm_path.exists():
        print(f"Error: VRM file not found: {vrm_path}")
        sys.exit(1)
    
    if not vrm_path.suffix.lower() in ['.gltf', '.glb', '.vrm']:
        print(f"Warning: File extension '{vrm_path.suffix}' is not typical for VRM files")
    
    try:
        # Create and run pipeline
        pipeline = VRMCapsulePipeline(str(vrm_path), args.output_dir)
        
        success = pipeline.run_complete_pipeline(
            max_capsules=args.max_capsules,
            timeout=args.timeout
        )
        
        if not success:
            print("\nPipeline failed. Check the error messages above.")
            sys.exit(1)
        
        print("\nPipeline completed successfully!")
        
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
