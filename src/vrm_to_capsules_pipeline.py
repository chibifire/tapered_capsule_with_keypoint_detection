#!/usr/bin/env python3
"""
Complete VRM to Tapered Capsules Pipeline.
Analyzes VRM mesh, runs constraint optimization, and generates Godot scenes.
"""

import os
import sys
import subprocess
import tempfile
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
    
    def run_single_optimization(self, capsule_count: int, timeout: int = 300, solver: str = "gecode") -> tuple[bool, str]:
        """Run a single optimization attempt with specified parameters."""
        
        # Generate constraint file for specific capsule count
        analyzer = VRMMeshAnalyzer()
        if not analyzer.load_vrm_file(str(self.vrm_path)):
            return False, "Failed to reload VRM file"
        
        temp_constraints_file = self.output_dir / f"{self.vrm_path.stem}_temp_{capsule_count}caps.dzn"
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
