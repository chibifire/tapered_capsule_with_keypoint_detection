"""
Tapered Capsule Public API
=========================

This module provides the main public API for the tapered capsule generation system.
It exposes key functionality for analyzing glTF2 skinned meshes, generating capsule constraints,
running optimizations, and creating glTF models with capsules.

Main Components:
- Skeleton Analysis: Analyze glTF2 skeletons and extract bone geometry
- Capsule Generation: Create capsule constraints for optimization
- Optimization: Run MiniZinc solvers to optimize capsule parameters
- GLTF Export: Generate glTF models with optimized capsules
- Complete Pipelines: End-to-end workflows for capsule generation

Example usage:
    from tapered_capsule import SkinnedCapsulePipeline
    
    # Analyze a glTF file and generate capsules
    pipeline = SkinnedCapsulePipeline()
    pipeline.load_gltf_and_analyze("model.gltf")
    pipeline.run_optimization(max_capsules=8)
    pipeline.generate_gltf_output("output.gltf")
"""

import sys
import argparse
from pathlib import Path

# Public API imports
from src.skinned_capsule_pipeline import SkinnedCapsulePipeline
from src.capsule_generator import CapsuleGenerator
from src.minizinc_to_gltf import GLTFCapsuleGenerator

# Public API classes
__all__ = [
    "SkinnedCapsulePipeline",
    "CapsuleGenerator",
    "GLTFCapsuleGenerator"
]

# Version information
__version__ = "1.0.0"
__author__ = "Capsule Generation Team"


def analyze_gltf_skeleton(model_path: str) -> SkinnedCapsulePipeline:
    """
    Analyze a glTF/GLB/VRM skinned mesh and extract bone geometry data.
    
    Args:
        model_path: Path to the glTF, GLB, or VRM file
        
    Returns:
        SkinnedCapsulePipeline instance with loaded data
    """
    pipeline = SkinnedCapsulePipeline()
    if pipeline.load_gltf_and_analyze(model_path):
        return pipeline
    else:
        raise RuntimeError(f"Failed to load model file: {model_path}")


def generate_capsules_from_model(model_path: str, output_path: str, 
                                max_capsules: int = 8, timeout: int = 30) -> bool:
    """
    Run the complete model to capsules pipeline.
    
    Args:
        model_path: Path to the glTF, GLB, or VRM file
        output_path: Path for output glTF file with capsules
        max_capsules: Maximum number of capsules to generate
        timeout: Timeout for optimization in seconds
        
    Returns:
        True if successful, False otherwise
    """
    pipeline = SkinnedCapsulePipeline()
    
    # Load and analyze model
    if not pipeline.load_gltf_and_analyze(model_path):
        return False
    
    # Run optimization
    if not pipeline.run_optimization(max_capsules, timeout):
        return False
    
    # Generate output
    return pipeline.generate_gltf_output(output_path)


def generate_skinned_capsules_from_results(model_path: str, results_path: str, 
                                          output_path: str, dzn_path: str = None,
                                          max_capsules: int = 25) -> bool:
    """
    Generate skinned capsules from model file and optimization results.
    
    Args:
        model_path: Path to the glTF, GLB, or VRM file
        results_path: Path to MiniZinc optimization results
        output_path: Path for output glTF file
        dzn_path: Path to DZN data file (optional)
        max_capsules: Maximum number of capsules
        
    Returns:
        True if successful, False otherwise
    """
    pipeline = SkinnedCapsulePipeline()
    
    # Load and analyze model
    if not pipeline.load_gltf_and_analyze(model_path):
        return False
    
    # Parse optimization results
    capsules = pipeline.parse_optimization_results(results_path, dzn_path)
    if not capsules:
        return False
    
    # Generate skinned capsules
    return pipeline.generate_skinned_capsules(capsules, output_path, model_path, dzn_path)


def main():
    """Main CLI entry point for the tapered capsule system."""
    parser = argparse.ArgumentParser(
        description="Generate tapered capsules for glTF/GLB/VRM skinned mesh skeletons",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tapered-capsule analyze model.vrm
  tapered-capsule generate model.glb --output output.gltf --max-capsules 8
  tapered-capsule from-results model.gltf results.txt output.gltf
        """
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Tapered Capsule Generator {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze model skeleton")
    analyze_parser.add_argument("input", help="Input model file (glTF, GLB, or VRM)")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate capsules from model")
    generate_parser.add_argument("input", help="Input model file (glTF, GLB, or VRM)")
    generate_parser.add_argument("--output", "-o", required=True, help="Output glTF file")
    generate_parser.add_argument("--max-capsules", "-n", type=int, default=8, 
                                help="Maximum number of capsules (default: 8)")
    generate_parser.add_argument("--timeout", "-t", type=int, default=30,
                                help="Optimization timeout in seconds (default: 30)")
    
    # From-results command
    results_parser = subparsers.add_parser("from-results", 
                                          help="Generate capsules from optimization results")
    results_parser.add_argument("input", help="Input model file (glTF, GLB, or VRM)")
    results_parser.add_argument("results", help="MiniZinc optimization results file")
    results_parser.add_argument("output", help="Output glTF file")
    results_parser.add_argument("--dzn", help="DZN data file (optional)")
    results_parser.add_argument("--max-capsules", "-n", type=int, default=25, 
                               help="Maximum number of capsules (default: 25)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == "analyze":
            print(f"Analyzing glTF file: {args.input}")
            pipeline = analyze_gltf_skeleton(args.input)
            print("Analysis completed successfully")
            return 0
            
        elif args.command == "generate":
            print(f"Generating capsules from: {args.input}")
            print(f"Output file: {args.output}")
            print(f"Max capsules: {args.max_capsules}")
            success = generate_capsules_from_model(
                args.input, args.output, args.max_capsules, args.timeout
            )
            if success:
                print("Capsule generation completed successfully")
                return 0
            else:
                print("Capsule generation failed")
                return 1
                
        elif args.command == "from-results":
            print(f"Generating capsules from results: {args.results}")
            print(f"Input glTF: {args.input}")
            print(f"Output file: {args.output}")
            success = generate_skinned_capsules_from_results(
                args.input, args.results, args.output, args.dzn, args.max_capsules
            )
            if success:
                print("Capsule generation completed successfully")
                return 0
            else:
                print("Capsule generation failed")
                return 1
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
