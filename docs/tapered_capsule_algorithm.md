# TAPERED CAPSULE OPTIMIZATION ALGORITHM

## PUBLIC API

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

## CAPSULE SIZING GUIDE

For optimal results, refer to the [Capsule Sizing Guide](docs/capsule_sizing_guide.md) which provides recommendations for the number of capsules to use for different types of avatars.

For a representative female avatar, start with **10 capsules** as a baseline:

```python
# Test with female avatar
tapered_capsule.generate_capsules_from_vrm('thirdparty/vrm_samples/vroid/fem_vroid.vrm', max_capsules=10)
```

## IMPLEMENTED PIPELINE

Complete implementation available in `coacd_capsule_pipeline.py`

### MESH LOADING

Load input mesh using GLTF parser

Support VRM1 GLTF format with skinned meshes

Extract vertex positions, normals, bone weights

### SKELETON-BASED MESH SEGMENTATION

Extract vertices associated with each bone based on skinning weights

Vertices with dominant bone influence are grouped together

Preserve vertex-bone associations for later processing

Maintain hierarchical ordering (parents before children)

### PER-BONE CONVEX DECOMPOSITION

Run coacd separately on each bone's vertex set

Generate convex hulls that respect anatomical boundaries

Each hull represents potential capsule coverage for specific bone

Preserve vertex-bone weight associations within each bone group

### CANDIDATE CAPSULE GENERATION

For each convex hull:

- Apply PCA to find longest axis (capsule orientation)

- Define endpoints p1, p2 along principal axis

- Calculate radii r1, r2 from vertex extents

- Create tapered capsule shape with dual radii

- Compute swing rotation to align with bone direction

- Determine twist rotation from bone orientation

- Calculate height as distance between endpoints

- Define radius_top and radius_bottom parameters

### SKELETON HIERARCHY PROCESSING

When generating capsules for skinned meshes with skeletal structures:

- Process joints in hierarchical order (parents before children)

- Start with root joints (e.g., hips) before processing descendants

- Maintain anatomical structure consistency during optimization

- Preserve bone direction vectors from parent to child relationships

- Apply hierarchical constraints to ensure proper capsule placement

- Consider joint dependencies when building coverage matrices

### WITNESS POINT SAMPLING

Sample thousands of points from mesh interior

Use for coverage verification in optimization

Ensure uniform distribution across volume

### COVERAGE MATRIX CONSTRUCTION

Check which capsules contain which witness points

Build boolean matrix: rows=capsules, columns=points

Entry=1 if capsule covers point, 0 otherwise

### MINIZINC DATA FORMATTING

Write capsule count, point count to .dzn file

Output coverage matrix in 2D array format

Include capsule parameters for solver access

- Position coordinates (x, y, z)

- Swing rotation parameters

- Twist rotation parameters

- Height values

- Radius_top and radius_bottom values

### SET-COVERING OPTIMIZATION

MiniZinc model solves for minimum capsule set

Objective: minimize capsules while maximizing coverage

Constraints: each point covered by at least one capsule

Solve for capsule parameters:

- Position coordinates (x, y, z)

- Swing rotation angles

- Twist rotation angles

- Height values

- Radius_top and radius_bottom values

Output: indices of selected optimal capsules

### RESULT PROCESSING

Extract parameters of selected capsules

Generate tapered capsule mesh geometry

Apply bone skinning from original weights

Export to GLTF format with flat hierarchy

## KEY FEATURES

### TAPERED CAPSULES

Dual radii r1, r2 for anatomically accurate shapes

Smooth transition between joint connections

Better volume representation than uniform cylinders

Solve for radius_top and radius_bottom parameters

Height parameter for precise dimension control

### ROTATION PARAMETERS

Swing rotation for bone direction alignment

Twist rotation for natural joint orientation

Full 3D orientation optimization

### BONE SKINNING PRESERVATION

Maintain vertex-bone weight associations

Transfer weights to optimized capsule geometry

Support skeletal animation in target engines

### HIERARCHY-INDEPENDENT STRUCTURE

Flat node organization for maximum compatibility

No parent-child relationships between capsules

Capsules positioned absolutely in world space

### CONSTRAINT-BASED OPTIMIZATION

MiniZinc solver ensures mathematical optimality

Set-covering formulation guarantees coverage

Scalable to different mesh complexities

## INPUT/OUTPUT SPECIFICATIONS

### INPUTS

- VRM1/GLTF skinned mesh file

- CoACD convex decomposition parameters

- Witness point sampling density

- MiniZinc solver configuration

### OUTPUTS

- Optimized capsule parameter set:

  - Position coordinates (x, y, z)

  - Swing rotation angles

  - Twist rotation angles

  - Height values

  - Radius_top and radius_bottom values

- GLTF file with capsule geometry

- Bone skinning weight transfer

- Coverage statistics and validation

## PERFORMANCE CHARACTERISTICS

### COMPUTATIONAL COMPLEXITY

- Convex decomposition: O(n log n) vertex count

- Coverage matrix: O(m×k) capsules×points

- MiniZinc solving: NP-hard set covering

- Mesh generation: O(p) capsule polygons

### MEMORY REQUIREMENTS

- Coverage matrix dominates memory usage

- Scales with witness point count squared

- Optimized for sparse matrix representation

### PARALLELIZATION

- Convex decomposition parallelizable

- Coverage checking parallelizable

- MiniZinc solver supports parallel execution

- Mesh generation parallelizable per capsule
