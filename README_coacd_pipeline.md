# CoACD-based Tapered Capsule Optimization Pipeline

This pipeline generates optimized tapered capsules from VRM avatars using CoACD convex decomposition and MiniZinc constraint solving. It uses the existing GLTF parser instead of trimesh for better integration with the project.

## Overview

The pipeline implements a per-bone convex decomposition approach that respects the skeletal structure of the character:

1. **Skeleton-based mesh segmentation** - Vertices are grouped by their dominant bone influence
2. **Per-bone convex decomposition** - CoACD is run separately on each bone's vertex set
3. **Candidate capsule generation** - Tapered capsules are generated from convex hulls using PCA
4. **Witness point sampling** - Points are sampled from the mesh interior for coverage verification
5. **Set-covering optimization** - MiniZinc solves for the minimum capsule set that covers all points
6. **GLTF export** - Optimized capsules are exported as a flat GLTF structure

## Installation

```bash
# Install required Python packages
pip install trimesh coacd numpy scikit-learn

# Install MiniZinc (https://www.minizinc.org/)
# On macOS: brew install minizinc
# On Ubuntu: sudo apt-get install minizinc
# On Windows: Download from https://www.minizinc.org/
```

## Usage

### Command Line Interface

```bash
# Run the complete pipeline
python coacd_capsule_pipeline.py input_avatar.vrm

# With custom parameters
python coacd_capsule_pipeline.py input_avatar.vrm \
  --threshold 0.05 \
  --points 5000 \
  --max-capsules 50 \
  --output-dir ./output
```

### Python API

```python
from coacd_capsule_pipeline import CoACDCapsulePipeline

# Create pipeline instance
pipeline = CoACDCapsulePipeline("input_avatar.vrm", output_dir="./output")

# Run complete pipeline
success = pipeline.run_complete_pipeline(
    coacd_threshold=0.05,
    witness_points=5000,
    max_capsules=50
)

if success:
    print("Pipeline completed successfully!")
```

## Pipeline Steps

1. **Mesh Loading** - Load VRM/GLTF mesh with existing GLTF parser
2. **Skeleton Extraction** - Extract bone weights and joint hierarchy
3. **Per-Bone Decomposition** - Run CoACD on each bone's vertex set
4. **Capsule Generation** - Create tapered capsules from convex hulls
5. **Witness Sampling** - Sample points for coverage verification
6. **Coverage Matrix** - Build capsule-point coverage relationships
7. **MiniZinc Data** - Generate constraint problem data file
8. **Optimization** - Solve set-covering problem with MiniZinc
9. **Result Processing** - Export selected capsules to GLTF

## Output Files

- `*_coacd_data.dzn` - MiniZinc data file for constraint solving
- `*_coacd_results.txt` - Optimization results from MiniZinc
- `*_coacd_capsules.gltf` - Optimized capsule geometry in GLTF format

## Key Features

### Tapered Capsules

- Dual radii for anatomically accurate shapes
- Smooth transitions between joint connections
- Better volume representation than uniform cylinders

### Bone Skinning Preservation

- Maintains vertex-bone weight associations
- Transfers weights to optimized capsule geometry
- Supports skeletal animation in target engines

### Hierarchy-Independent Structure

- Flat node organization for maximum compatibility
- No parent-child relationships between capsules
- Capsules positioned absolutely in world space

### Constraint-Based Optimization

- MiniZinc solver ensures mathematical optimality
- Set-covering formulation guarantees coverage
- Scalable to different mesh complexities

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
