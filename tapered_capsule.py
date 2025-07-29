"""
Tapered Capsule Public API
=========================

This module provides the main public API for the tapered capsule generation system.
It exposes key functionality for analyzing VRM meshes, generating capsule constraints,
running optimizations, and creating glTF models with capsules.

Main Components:
- VRM Analysis: Analyze VRM meshes and extract bone geometry
- Capsule Generation: Create capsule constraints for optimization
- Optimization: Run MiniZinc solvers to optimize capsule parameters
- GLTF Export: Generate glTF models with optimized capsules
- Complete Pipelines: End-to-end workflows for capsule generation

Example usage:
    from tapered_capsule import VRMCapsulePipeline
    
    # Analyze a VRM file and generate capsules
    pipeline = VRMCapsulePipeline("model.vrm")
    pipeline.run_complete_pipeline(max_capsules=8)
"""

# Public API imports
from src.vrm_mesh_analyzer import VRMMeshAnalyzer
from src.vrm_to_capsules_pipeline import VRMCapsulePipeline
from src.skinned_capsule_pipeline import SkinnedCapsulePipeline
from src.capsule_generator import CapsuleGenerator
from src.minizinc_to_gltf import GLTFCapsuleGenerator

# Public API classes
__all__ = [
    "VRMMeshAnalyzer",
    "VRMCapsulePipeline", 
    "SkinnedCapsulePipeline",
    "CapsuleGenerator",
    "GLTFCapsuleGenerator"
]

# Version information
__version__ = "1.0.0"
__author__ = "Capsule Generation Team"


def analyze_vrm_mesh(vrm_path: str, max_capsules: int = 25) -> VRMMeshAnalyzer:
    """
    Analyze a VRM mesh and extract bone geometry data.
    
    Args:
        vrm_path: Path to the VRM file
        max_capsules: Maximum number of capsules to consider
        
    Returns:
        VRMMeshAnalyzer instance with loaded data
    """
    analyzer = VRMMeshAnalyzer()
    if analyzer.load_vrm_file(vrm_path):
        return analyzer
    else:
        raise RuntimeError(f"Failed to load VRM file: {vrm_path}")


def generate_capsules_from_vrm(vrm_path: str, max_capsules: int = 8, timeout: int = 30) -> bool:
    """
    Run the complete VRM to capsules pipeline.
    
    Args:
        vrm_path: Path to the VRM file
        max_capsules: Maximum number of capsules to generate
        timeout: Timeout for optimization in seconds
        
    Returns:
        True if successful, False otherwise
    """
    pipeline = VRMCapsulePipeline(vrm_path)
    return pipeline.run_complete_pipeline(max_capsules, timeout)


def generate_skinned_capsules_from_vrm(vrm_path: str, results_path: str, 
                                     output_path: str, dzn_path: str = None,
                                     max_capsules: int = 25) -> bool:
    """
    Generate skinned capsules from VRM file and optimization results.
    
    Args:
        vrm_path: Path to the VRM file
        results_path: Path to MiniZinc optimization results
        output_path: Path for output glTF file
        dzn_path: Path to DZN data file (optional)
        max_capsules: Maximum number of capsules
        
    Returns:
        True if successful, False otherwise
    """
    pipeline = SkinnedCapsulePipeline()
    
    # Load and analyze VRM
    if not pipeline.load_vrm_and_analyze(vrm_path):
        return False
    
    # Parse optimization results
    capsules = pipeline.parse_optimization_results(results_path, dzn_path)
    if not capsules:
        return False
    
    # Generate skinned capsules
    return pipeline.generate_skinned_capsules(capsules, output_path, vrm_path, dzn_path)
