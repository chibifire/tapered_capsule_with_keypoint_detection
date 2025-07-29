# Tapered Capsule Generation Pipeline

This pipeline implements an optimization algorithm for generating anatomically accurate tapered capsules from skinned mesh data. It includes multiple approaches for capsule generation, including CoACD (Connected Components Decimation) for convex decomposition and constraint-based optimization using MiniZinc.

## Public API

The pipeline now provides a clean public API through the `tapered_capsule` module:

```python
import tapered_capsule

# Analyze a VRM file
analyzer = tapered_capsule.VRMMeshAnalyzer()
analyzer.load_vrm_file('model.vrm')

# Run complete pipeline
tapered_capsule.generate_capsules_from_vrm('model.vrm', max_capsules=8)

# Generate skinned capsules from results
tapered_capsule.generate_skinned_capsules_from_vrm(
    'model.vrm', 'results.txt', 'output.gltf')
```

### Public API Components

- `VRMMeshAnalyzer`: Analyze VRM meshes and extract bone geometry
- `VRMCapsulePipeline`: Complete pipeline from VRM to optimized capsules
- `SkinnedCapsulePipeline`: Pipeline with skinning weight transfer
- `CapsuleGenerator`: Generate capsule constraints for optimization
- `GLTFCapsuleGenerator`: Convert optimization results to glTF format

### Public API Functions

- `analyze_vrm_mesh()`: Analyze a VRM mesh and extract bone geometry data
- `generate_capsules_from_vrm()`: Run the complete VRM to capsules pipeline
- `generate_skinned_capsules_from_vrm()`: Generate skinned capsules from VRM file and optimization results

## Overview

The pipeline takes a VRM/GLTF skinned mesh as input and produces optimized tapered capsules that accurately represent the mesh volume while minimizing the number of capsules needed for coverage.

## Algorithm Pipeline

1. **Mesh Loading**: Load input mesh using trimesh library with support for VRM1 GLTF format
2. **Skeleton-based Mesh Segmentation**: Extract vertices associated with each bone based on skinning weights
3. **Per-bone Convex Decomposition**: Run CoACD separately on each bone's vertex set
4. **Candidate Capsule Generation**: For each convex hull, generate tapered capsule parameters
5. **Witness Point Sampling**: Sample thousands of points from mesh interior for coverage verification
6. **Coverage Matrix Construction**: Check which capsules contain which witness points
7. **MiniZinc Data Formatting**: Write capsule parameters and coverage matrix to .dzn file
8. **Set-covering Optimization**: Use MiniZinc to solve for minimum capsule set
9. **Result Processing**: Generate tapered capsule mesh geometry and export to GLTF

## Key Features

### Tapered Capsules
- Dual radii (r1, r2) for anatomically accurate shapes
- Smooth transition between joint connections
- Better volume representation than uniform cylinders

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
# Install required dependencies
pip install numpy scikit-learn trimesh coacd

# Install MiniZinc solver (https://www.minizinc.org/)
# Follow instructions at https://www.minizinc.org/doc-2.7.6/en/installation.html
```

## Usage

```bash
# Run the complete pipeline
python3 coacd_capsule_pipeline.py input.vrm

# With custom parameters
python3 coacd_capsule_pipeline.py input.vrm --threshold 0.03 --points 10000 --max-capsules 30

# Output files will be generated in the same directory as the input file:
# - input_coacd_data.dzn: MiniZinc data file
# - input_coacd_results.txt: Optimization results
# - input_coacd_capsules.gltf: Optimized capsule geometry
```

## Pipeline Components

### coacd_capsule_pipeline.py
Main pipeline implementation that orchestrates the entire optimization process.

### coacd_capsule_model.mzn
MiniZinc model for set-covering optimization of capsule selection.

### minizinc_to_gltf.py
Converter that transforms MiniZinc optimization results into GLTF capsule geometry.

## Algorithm Details

### Skeleton-based Segmentation
Vertices are grouped by their dominant bone influence (highest skinning weight), allowing for anatomically meaningful convex decomposition.

### CoACD Convex Decomposition
CoACD is run separately on each bone's vertex set to generate convex hulls that respect anatomical boundaries.

### Tapered Capsule Generation
For each convex hull:
- PCA finds the longest axis (capsule orientation)
- Endpoints are determined by vertex projections
- Radii are calculated from vertex extents perpendicular to axis
- Swing and twist rotations align with bone directions

### Coverage Optimization
A set-covering problem is formulated where:
- Each witness point must be covered by at least one capsule
- The objective is to minimize the number of selected capsules
- MiniZinc solves this NP-hard optimization problem

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

## Customization

The pipeline can be customized by adjusting:
- CoACD decomposition threshold
- Witness point sampling density
- Maximum number of capsules
- MiniZinc solver parameters

## Troubleshooting

### Common Issues
1. **CoACD installation problems**: Ensure all dependencies are installed correctly
2. **MiniZinc not found**: Verify MiniZinc is in your PATH
3. **Memory issues**: Reduce witness point count or use fewer capsules
4. **No capsules generated**: Check input mesh has sufficient vertices per bone

### Debugging
- Enable verbose output with additional print statements
- Check intermediate files (.dzn, .txt) for optimization data
- Validate input mesh with mesh analysis tools
