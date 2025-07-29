MINIZINC3 DATA REQUIREMENTS FOR TAPERED CAPSULE OPTIMIZATION

OBJECTIVE: Define exact data format and structure needed for MiniZinc3 constraint solver to optimize tapered capsule placement.

RESPONSIBILITY: Specify data file format, variable bounds, and constraint parameters for space-maximal minimal-count optimization.

MINIZINC3 DATA FILE FORMAT (.dzn)

MiniZinc3 requires data file with .dzn extension containing parameter values.

All arrays must be 1-indexed (MiniZinc convention).

Data types must match model variable declarations exactly.

Comments allowed using % symbol for documentation.

REQUIRED PARAMETERS FOR CONSTRAINT PROBLEM

% Problem dimensions
int: num_bones;           % Number of VRM bones (typically 20-30)
int: max_capsules;        % Maximum capsules allowed (optimization variable)
int: num_vertices;        % Total mesh vertices for coverage calculation

% Spatial bounds from VRM mesh
array[1..3] of float: mesh_min_bounds;    % Minimum X,Y,Z coordinates
array[1..3] of float: mesh_max_bounds;    % Maximum X,Y,Z coordinates
float: total_mesh_volume;                 % Total volume for coverage objective

% Bone hierarchy and measurements
array[1..num_bones] of string: bone_names;
array[1..num_bones] of int: bone_parents;      % Parent bone indices (-1 for root)
array[1..num_bones, 1..3] of float: bone_positions;  % X,Y,Z positions
array[1..num_bones] of float: bone_lengths;          % Bone lengths
array[1..num_bones, 1..3] of float: bone_orientations; % Rotation angles

ANTHROPOMETRIC CONSTRAINTS FROM JAPANESE DATA

% From AIST database - constrains capsule dimensions
float: male_stature_mean = 1.714;
float: male_stature_std = 0.055;
float: female_stature_mean = 1.594;
float: female_stature_std = 0.049;

% Proportional ratios for capsule radius bounds
array[1..num_bones] of float: min_radius_ratios;  % Minimum R1,R2 as ratio of bone length
array[1..num_bones] of float: max_radius_ratios;  % Maximum R1,R2 as ratio of bone length

SPATIAL OCCUPANCY GRID FOR COVERAGE

% 3D grid for volume coverage calculation
int: grid_resolution;                              % Grid cells per dimension
array[1..grid_resolution, 1..grid_resolution, 1..grid_resolution] of bool: occupancy_grid;
float: grid_cell_volume;                          % Volume per grid cell

BONE INFLUENCE ZONES

% Defines where capsules can be placed based on skinning weights
array[1..num_bones, 1..3] of float: influence_centers;    % Center of influence zone
array[1..num_bones, 1..3] of float: influence_extents;    % Size of influence zone
array[1..num_bones] of float: influence_volumes;          % Volume of influence region

OPTIMIZATION WEIGHTS

% Multi-objective optimization parameters
float: coverage_weight = 1.0;        % Weight for volume coverage objective
float: count_penalty = 0.1;          % Penalty for each additional capsule
float: overlap_penalty = 10.0;       % Penalty for capsule overlaps

EXAMPLE DATA FILE STRUCTURE (constraint_data.dzn)

% VRM Tapered Capsule Optimization Data
% Generated from Godot VRM scene analysis

% Problem dimensions
num_bones = 20;
max_capsules = 15;
num_vertices = 8492;

% Spatial bounds
mesh_min_bounds = [-0.5, -0.1, -0.3];
mesh_max_bounds = [0.5, 1.8, 0.3];
total_mesh_volume = 0.0847;

% Complete VRM bone hierarchy (all standard bones)
bone_names = [
  % Core torso and head
  "hips", "spine", "chest", "upperChest", "neck", "head",
  % Left leg
  "leftUpperLeg", "leftLowerLeg", "leftFoot", "leftToes",
  % Right leg  
  "rightUpperLeg", "rightLowerLeg", "rightFoot", "rightToes",
  % Left arm
  "leftShoulder", "leftUpperArm", "leftLowerArm", "leftHand",
  % Right arm
  "rightShoulder", "rightUpperArm", "rightLowerArm", "rightHand"
];

bone_parents = [
  -1,  % hips (root)
  1,   % spine -> hips
  2,   % chest -> spine
  3,   % upperChest -> chest
  4,   % neck -> upperChest
  5,   % head -> neck
  1,   % leftUpperLeg -> hips
  7,   % leftLowerLeg -> leftUpperLeg
  8,   % leftFoot -> leftLowerLeg
  9,   % leftToes -> leftFoot
  1,   % rightUpperLeg -> hips
  11,  % rightLowerLeg -> rightUpperLeg
  12,  % rightFoot -> rightLowerLeg
  13,  % rightToes -> rightFoot
  4,   % leftShoulder -> upperChest
  15,  % leftUpperArm -> leftShoulder
  16,  % leftLowerArm -> leftUpperArm
  17,  % leftHand -> leftLowerArm
  4,   % rightShoulder -> upperChest
  19,  % rightUpperArm -> rightShoulder
  20,  % rightLowerArm -> rightUpperArm
  21   % rightHand -> rightLowerArm
];

bone_positions = [
  % Torso and head (from Japanese anthropometric data)
  [0.0, 0.800, 0.0],    % hips at crotch height
  [0.0, 1.017, 0.0],    % spine
  [0.0, 1.234, 0.0],    % chest
  [0.0, 1.451, 0.0],    % upperChest
  [0.0, 1.556, 0.0],    % neck
  [0.0, 1.714, 0.0],    % head at full stature
  % Left leg
  [-0.078, 0.800, 0.0], % leftUpperLeg (hip width offset)
  [-0.078, 0.397, 0.0], % leftLowerLeg
  [-0.078, 0.063, 0.0], % leftFoot
  [-0.078, 0.0, 0.0],   % leftToes
  % Right leg (symmetrical)
  [0.078, 0.800, 0.0],  % rightUpperLeg
  [0.078, 0.397, 0.0],  % rightLowerLeg
  [0.078, 0.063, 0.0],  % rightFoot
  [0.078, 0.0, 0.0],    % rightToes
  % Left arm
  [-0.195, 1.407, 0.0], % leftShoulder (shoulder width)
  [-0.487, 1.407, 0.0], % leftUpperArm
  [-0.779, 1.407, 0.0], % leftLowerArm
  [-0.950, 1.407, 0.0], % leftHand
  % Right arm (symmetrical)
  [0.195, 1.407, 0.0],  % rightShoulder
  [0.487, 1.407, 0.0],  % rightUpperArm
  [0.779, 1.407, 0.0],  % rightLowerArm
  [0.950, 1.407, 0.0]   % rightHand
];

bone_lengths = [
  0.0,     % hips (root, no length)
  0.217,   % spine
  0.217,   % chest
  0.217,   % upperChest
  0.105,   % neck
  0.157,   % head
  0.403,   % leftUpperLeg
  0.334,   % leftLowerLeg
  0.063,   % leftFoot
  0.030,   % leftToes
  0.403,   % rightUpperLeg (symmetrical)
  0.334,   % rightLowerLeg
  0.063,   % rightFoot
  0.030,   % rightToes
  0.156,   % leftShoulder
  0.292,   % leftUpperArm
  0.292,   % leftLowerArm
  0.171,   % leftHand
  0.156,   % rightShoulder (symmetrical)
  0.292,   % rightUpperArm
  0.292,   % rightLowerArm
  0.171    % rightHand
];

bone_orientations = [
  [0.0, 0.0, 0.0],     % hips
  [0.0, 0.0, 0.0],     % spine
  [0.0, 0.0, 0.0],     % chest
  [0.0, 0.0, 0.0],     % upperChest
  [0.0, 0.0, 0.0],     % neck
  [0.0, 0.0, 0.0],     % head
  [0.0, 0.0, -15.0],   % leftUpperLeg (slight outward angle)
  [0.0, 0.0, 0.0],     % leftLowerLeg
  [0.0, 0.0, 0.0],     % leftFoot
  [0.0, 0.0, 0.0],     % leftToes
  [0.0, 0.0, 15.0],    % rightUpperLeg (symmetrical)
  [0.0, 0.0, 0.0],     % rightLowerLeg
  [0.0, 0.0, 0.0],     % rightFoot
  [0.0, 0.0, 0.0],     % rightToes
  [0.0, 0.0, 30.0],    % leftShoulder (outward slope)
  [0.0, 0.0, -90.0],   % leftUpperArm (T-pose)
  [0.0, 0.0, 0.0],     % leftLowerArm
  [0.0, 0.0, 0.0],     % leftHand
  [0.0, 0.0, -30.0],   % rightShoulder (symmetrical)
  [0.0, 0.0, 90.0],    % rightUpperArm (T-pose)
  [0.0, 0.0, 0.0],     % rightLowerArm
  [0.0, 0.0, 0.0]      % rightHand
];

% Radius constraints (as ratios of bone length, bone-specific)
min_radius_ratios = [
  0.00,  % hips (root)
  0.12,  % spine (thick torso)
  0.15,  % chest
  0.12,  % upperChest
  0.08,  % neck (thin)
  0.20,  % head (large)
  0.18,  % leftUpperLeg (thick thigh)
  0.12,  % leftLowerLeg (calf)
  0.15,  % leftFoot
  0.08,  % leftToes (thin)
  0.18,  % rightUpperLeg (symmetrical)
  0.12,  % rightLowerLeg
  0.15,  % rightFoot
  0.08,  % rightToes
  0.10,  % leftShoulder
  0.12,  % leftUpperArm
  0.08,  % leftLowerArm (forearm)
  0.12,  % leftHand
  0.10,  % rightShoulder (symmetrical)
  0.12,  % rightUpperArm
  0.08,  % rightLowerArm
  0.12   % rightHand
];

max_radius_ratios = [
  0.00,  % hips (root)
  0.35,  % spine
  0.40,  % chest (broad)
  0.35,  % upperChest
  0.25,  % neck
  0.45,  % head
  0.35,  % leftUpperLeg
  0.25,  % leftLowerLeg
  0.30,  % leftFoot
  0.20,  % leftToes
  0.35,  % rightUpperLeg (symmetrical)
  0.25,  % rightLowerLeg
  0.30,  % rightFoot
  0.20,  % rightToes
  0.25,  % leftShoulder
  0.28,  % leftUpperArm
  0.22,  % leftLowerArm
  0.25,  % leftHand
  0.25,  % rightShoulder (symmetrical)
  0.28,  % rightUpperArm
  0.22,  % rightLowerArm
  0.25   % rightHand
];

% Spatial occupancy (simplified 8x8x8 grid example)
grid_resolution = 8;
occupancy_grid = [true, false, true, ...];  % Flattened 3D array
grid_cell_volume = 0.001;

% Influence zones
influence_centers = [
  [0.0, 0.9, 0.0],    % hips influence center
  [0.0, 1.1, 0.0],    % spine influence center
  [0.0, 1.3, 0.0]     % chest influence center
];
influence_extents = [
  [0.2, 0.15, 0.2],   % hips influence size
  [0.15, 0.1, 0.15],  % spine influence size
  [0.25, 0.1, 0.2]    % chest influence size
];
influence_volumes = [0.006, 0.0023, 0.005];

CONSTRAINT MODEL REQUIREMENTS (tapered_capsule_optimization.mzn)

Model file must define decision variables matching data parameters.

Include domain constraints using data bounds.

Define objective function using coverage and count weights.

Implement non-overlap constraints between active capsules.

DECISION VARIABLES IN MODEL

% Capsule parameters (decision variables)
array[1..max_capsules, 1..3] of var float: capsule_positions;
array[1..max_capsules, 1..3] of var -180.0..180.0: capsule_orientations;
array[1..max_capsules] of var 0.01..2.0: capsule_lengths;
array[1..max_capsules, 1..2] of var 0.005..0.5: capsule_radii;
array[1..max_capsules] of var bool: capsule_active;

CONSTRAINT EXAMPLES USING DATA

% Position bounds using mesh data
constraint forall(i in 1..max_capsules)(
    if capsule_active[i] then
        capsule_positions[i,1] >= mesh_min_bounds[1] /\
        capsule_positions[i,1] <= mesh_max_bounds[1] /\
        capsule_positions[i,2] >= mesh_min_bounds[2] /\
        capsule_positions[i,2] <= mesh_max_bounds[2] /\
        capsule_positions[i,3] >= mesh_min_bounds[3] /\
        capsule_positions[i,3] <= mesh_max_bounds[3]
    endif
);

% Radius bounds using anthropometric ratios
constraint forall(i in 1..max_capsules, j in 1..2)(
    if capsule_active[i] then
        capsule_radii[i,j] >= capsule_lengths[i] * min_radius_ratios[1] /\
        capsule_radii[i,j] <= capsule_lengths[i] * max_radius_ratios[1]
    endif
);

OBJECTIVE FUNCTION USING DATA

% Multi-objective: maximize coverage, minimize count
var float: coverage_score = sum(i in 1..max_capsules)(
    if capsule_active[i] then calculate_coverage(i) else 0.0 endif
);
var int: active_count = sum(i in 1..max_capsules)(capsule_active[i]);

solve maximize (coverage_weight * coverage_score - count_penalty * active_count);

DATA GENERATION FROM GODOT

Use Godot VRM extraction script to generate .dzn file automatically.

Validate data ranges and array dimensions before solver execution.

Include metadata comments for debugging and verification.

Export both data file and corresponding model file for complete problem definition.

SOLVER EXECUTION COMMAND

minizinc --solver COIN-BC tapered_capsule_optimization.mzn constraint_data.dzn

Output provides optimal capsule parameters for Godot mesh generation.

Solution includes capsule positions, orientations, lengths, radii, and activation flags.

VALIDATION REQUIREMENTS

Data file must parse without MiniZinc syntax errors.

All array dimensions must match model variable declarations.

Floating point precision sufficient for geometric calculations.

Constraint bounds must be feasible (non-empty solution space).
