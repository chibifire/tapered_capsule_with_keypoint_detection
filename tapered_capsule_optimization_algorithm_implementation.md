# Tapered Capsule Optimization Algorithm Implementation

## Overview

This document describes the implementation of a CoACD-based tapered capsule optimization algorithm that generates anatomically accurate capsules from skinned mesh data. The implementation follows the algorithm described in the specification document while addressing practical considerations for real-world usage.

## Implementation Architecture

The implementation is organized into several key components:

### 1. CoACD Pipeline (`coacd_capsule_pipeline.py`)

The main pipeline orchestrates the entire optimization process:

#### Key Features:
- **Skeleton-based Mesh Segmentation**: Groups vertices by dominant bone influence for anatomically meaningful decomposition
- **Per-bone Convex Decomposition**: Uses CoACD to generate convex hulls that respect anatomical boundaries
- **Robust Error Handling**: Implements fallback strategies when CoACD fails on point clouds
- **Tapered Capsule Generation**: Creates capsules with dual radii for anatomical accuracy
- **Set-covering Optimization**: Integrates with MiniZinc for mathematical optimization

#### Pipeline Steps:
1. Mesh Loading and Skeleton Extraction
2. Vertex Grouping by Bone Influence
3. Per-bone CoACD Decomposition with Fallbacks
4. Candidate Capsule Generation with PCA-based Orientation
5. Witness Point Sampling for Coverage Verification
6. Coverage Matrix Construction for Optimization
7. MiniZinc Data File Generation
8. Optimization Result Processing and GLTF Export

### 2. MiniZinc Integration

The implementation uses MiniZinc for constraint-based optimization:

#### Model Features:
- **Set-covering Formulation**: Ensures all witness points are covered by at least one capsule
- **Cardinality Minimization**: Minimizes the number of selected capsules
- **Constraint Satisfaction**: Maintains coverage requirements while optimizing selection

### 3. GLTF Export (`minizinc_to_gltf.py`)

Generates optimized capsule geometry in GLTF format:

#### Key Features:
- **Tapered Capsule Mesh Generation**: Creates accurate tapered capsule geometry
- **Bone Skinning Preservation**: Maintains vertex-bone weight associations
- **Flat Hierarchy Structure**: Ensures maximum compatibility with target engines
- **Proper Transformations**: Applies local node transformations for correct positioning

## Technical Implementation Details

### Skeleton-based Segmentation

The algorithm groups vertices by their dominant bone influence:
- For each vertex, finds the bone with the highest skinning weight
- Groups vertices with bone influence > 0.1 threshold
- Skips vertices with very low bone influence

### CoACD Convex Decomposition

Per-bone convex decomposition with robust error handling:
- Runs CoACD separately on each bone's vertex set
- Implements fallback to simple convex hulls when CoACD fails
- Handles point cloud limitations gracefully
- Uses conservative vertex count thresholds

### Tapered Capsule Generation

For each convex hull, generates anatomically accurate capsules:
- Uses PCA to find the longest axis (capsule orientation)
- Calculates endpoints by vertex projections
- Determines radii from vertex extents perpendicular to axis
- Uses 90th percentile for robust radius estimation
- Calculates swing and twist rotations for proper alignment

### Coverage Optimization

Set-covering optimization with mathematical guarantees:
- Samples witness points from mesh interior
- Builds boolean coverage matrix
- Formulates constraint satisfaction problem
- Uses MiniZinc for NP-hard optimization

## Performance Considerations

### Computational Complexity
- Convex decomposition: O(n log n) vertex count
- Coverage matrix: O(m×k) capsules×points
- MiniZinc solving: NP-hard set covering
- Mesh generation: O(p) capsule polygons

### Memory Requirements
- Coverage matrix dominates memory usage
- Scales with witness point count squared
- Optimized for sparse matrix representation

### Parallelization Opportunities
- Convex decomposition parallelizable per bone
- Coverage checking parallelizable per capsule
- MiniZinc solver supports parallel execution
- Mesh generation parallelizable per capsule

## Error Handling and Robustness

### CoACD Integration
- Graceful degradation to convex hulls when CoACD fails
- Vertex count validation before decomposition
- Exception handling for library import issues

### Data Validation
- Bounds checking for all numerical values
- Dimension validation for matrix operations
- Fallback mechanisms for missing data

### File I/O
- Proper resource cleanup with `__del__` method
- Path validation and directory creation
- Error reporting for file operations

## Customization and Extensibility

### Pipeline Parameters
- CoACD decomposition threshold
- Witness point sampling density
- Maximum capsule count
- Vertex grouping thresholds

### Extension Points
- Custom convex decomposition algorithms
- Alternative optimization solvers
- Different capsule parameterization methods
- Enhanced bone influence analysis

## Usage Examples

### Command Line Usage
```bash
# Basic usage
python3 coacd_capsule_pipeline.py input.vrm

# With custom parameters
python3 coacd_capsule_pipeline.py input.vrm --threshold 0.03 --points 10000 --max-capsules 30
```

### Programmatic Usage
```python
from coacd_capsule_pipeline import CoACDCapsulePipeline

pipeline = CoACDCapsulePipeline("input.vrm")
success = pipeline.run_complete_pipeline(
    coacd_threshold=0.05,
    witness_points=5000,
    max_capsules=50
)
```

## Output Files

### Generated Artifacts
- `input_coacd_data.dzn`: MiniZinc data file with optimization parameters
- `input_coacd_results.txt`: Optimization results with selected capsules
- `input_coacd_capsules.gltf`: Optimized capsule geometry in GLTF format

### Data Format
- Position coordinates (x, y, z)
- Swing rotation angles
- Twist rotation angles
- Height values
- Radius_top and radius_bottom values

## Validation and Testing

### Unit Tests
- Point-in-capsule testing
- Pipeline initialization verification
- Component integration testing

### Validation Features
- Coverage statistics reporting
- Witness point coverage verification
- Capsule parameter validation

## Future Improvements

### Algorithm Enhancements
- Improved bone influence analysis
- Enhanced capsule parameterization
- Better witness point sampling strategies
- Advanced optimization formulations

### Performance Optimizations
- Parallel processing for decomposition
- Memory-efficient matrix operations
- Caching for repeated computations
- Streaming for large datasets

### Integration Improvements
- Additional file format support
- Enhanced VRM compatibility
- Better error reporting
- Progress indication for long operations

## Conclusion

This implementation provides a robust, production-ready solution for generating optimized tapered capsules from skinned mesh data. By combining CoACD-based convex decomposition with mathematical optimization, it produces anatomically accurate capsules that minimize count while ensuring complete coverage. The modular architecture and comprehensive error handling make it suitable for integration into larger systems and adaptable to various use cases.
