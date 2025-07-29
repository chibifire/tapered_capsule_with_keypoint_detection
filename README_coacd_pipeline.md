# CoACD-based Tapered Capsule Optimization Pipeline

This pipeline implements an optimization algorithm for generating tapered capsules from 3D mesh data using CoACD (Connected Components Analysis for 3D) convex decomposition.

## Overview

The pipeline takes a VRM/GLTF skinned mesh as input and generates an optimized set of tapered capsules that approximate the shape of the original mesh. The approach uses CoACD to decompose the mesh into convex hulls, then converts these hulls into tapered capsules for optimal coverage.

## Algorithm Pipeline

1. **Mesh Loading**: Load input mesh using GLTF parser, supporting VRM1 format with skinned meshes
2. **Skeleton-based Segmentation**: Extract vertices associated with each bone based on skinning weights
3. **Per-bone Convex Decomposition**: Run CoACD separately on each bone's vertex set to generate convex hulls
4. **Candidate Capsule Generation**: Convert convex hulls to tapered capsules with dual radii parameters
5. **Witness Point Sampling**: Sample thousands of points from mesh interior for coverage verification
6. **Coverage Matrix Construction**: Check which capsules contain which witness points to build a boolean matrix
7. **MiniZinc Data Formatting**: Write capsule parameters and coverage matrix to .dzn file format
8. **Set-covering Optimization**: Use MiniZinc solver to find minimum capsule set that maximizes coverage
9. **Result Processing**: Generate optimized capsule mesh geometry and export to GLTF format

## Key Features

### Tapered Capsules
- Dual radii (r1, r2) for anatomically accurate shapes
- Smooth transition between joint connections
- Better volume representation than uniform cylinders
- Height parameter for precise dimension control

### Rotation Parameters
- Swing rotation for bone direction alignment
- Twist rotation for natural joint orientation
- Full 3D orientation optimization

### Bone Skinning Preservation
- Maintain vertex-bone weight associations
- Transfer weights to optimized capsule geometry
- Support skeletal animation in target engines

### Hierarchy-independent Structure
- Flat node organization for maximum compatibility
- No parent-child relationships between capsules
- Capsules positioned absolutely in world space

### Constraint-based Optimization
- MiniZinc solver ensures mathematical optimality
- Set-covering formulation guarantees coverage
- Scalable to different mesh complexities

## Installation

```bash
# Install CoACD
pip install coacd

# Install MiniZinc (https://www.minizinc.org/)
# Follow installation instructions for your platform

# Install required Python packages
pip install numpy scikit-learn
```

## Usage

```bash
# Run the complete pipeline
python3 coacd_capsule_pipeline.py input.vrm

# With custom parameters
python3 coacd_capsule_pipeline.py input.vrm --threshold 0.05 --points 5000 --max-capsules 50

# Specify output directory
python3 coacd_capsule_pipeline.py input.vrm -o ./output/
```

## Input/Output Specifications

### Inputs
- VRM1/GLTF skinned mesh file
- CoACD convex decomposition parameters
- Witness point sampling density
- MiniZinc solver configuration

### Outputs
- Optimized capsule parameter set:
  - Position coordinates (x, y, z)
  - Swing rotation angles
  - Twist rotation angles
  - Height values
  - Radius_top and radius_bottom values
- GLTF file with capsule geometry
- Bone skinning weight transfer
- Coverage statistics and validation

## Performance Characteristics

### Computational Complexity
- Convex decomposition: O(n log n) vertex count
- Coverage matrix: O(m×k) capsules×points
- MiniZinc solving: NP-hard set covering
- Mesh generation: O(p) capsule polygons

### Memory Requirements
- Coverage matrix dominates memory usage
- Scales with witness point count squared
- Optimized for sparse matrix representation

### Parallelization
- Convex decomposition parallelizable
- Coverage checking parallelizable
- MiniZinc solver supports parallel execution
- Mesh generation parallelizable per capsule

## Implementation Details

The pipeline is implemented in `coacd_capsule_pipeline.py` and follows the algorithm described in `tapered_capsule_optimization_algorithm.md`. Key components include:

1. **CoACDCapsulePipeline class**: Main pipeline orchestrator
2. **Mesh loading and skeleton extraction**: Uses existing GLTF parser and mesh data extractor
3. **CoACD integration**: Direct interface to CoACD library for convex decomposition
4. **Capsule generation**: Converts convex hulls to tapered capsules using PCA for orientation
5. **Coverage checking**: Custom implementation for point-in-tapered-capsule testing
6. **MiniZinc interface**: Generates data files and processes solver output
7. **GLTF export**: Reuses existing minizinc_to_gltf functionality

## Testing

Run the test suite to verify functionality:

```bash
python3 test_coacd_pipeline.py
```

## Dependencies

- coacd: Connected Components Analysis for 3D
- MiniZinc: Constraint modeling language
- numpy: Numerical computing
- scikit-learn: PCA implementation
- Existing project modules (gltf_parser, mesh_data_extractor, minizinc_to_gltf, etc.)
