% VRM Tapered Capsule Optimization Problem - Gecode Version
% Addresses hierarchy bugs, scaling issues, and constraint complexity
% Designed for reliable solving with Gecode

include "globals.mzn";

% Parameters from VRM mesh analysis (float values)
int: n_capsules;  % Number of capsules to optimize
array[1..n_capsules, 1..3] of float: bone_centers;  % Bone geometry centers
array[1..n_capsules, 1..3] of float: bone_sizes;    % Bone geometry extents
array[1..n_capsules, 1..9] of float: bone_rotations; % 3x3 rotation matrices
array[1..n_capsules, 1..3] of float: bone_directions; % Bone direction vectors
array[1..n_capsules] of string: bone_names;         % Bone names from VRM
array[1..3] of float: min_pos;  % Global mesh bounds
array[1..3] of float: max_pos;  % Global mesh bounds
float: max_radius;  % Maximum allowed capsule radius
float: max_length;  % Maximum allowed capsule length

% Reduced optimization weights for faster convergence
int: coverage_weight = 50;
int: count_penalty = 2;
int: overlap_penalty = 100;

% Decision variables with conservative bounds to prevent overflow
% Add explicit bounds to prevent Gecode "Number out of limits" errors
array[1..n_capsules, 1..3] of var -1000.0..1000.0: capsule_positions;  % Float positions
array[1..n_capsules] of var 0.0..1000.0: capsule_lengths;          % Float lengths
array[1..n_capsules] of var 0.0..1000.0: capsule_radii;            % Float radii
array[1..n_capsules] of var bool: capsule_active;

% Position bounds constraints (capsules should be near their bone centers)
constraint forall(i in 1..n_capsules, j in 1..3)(
    if capsule_active[i] then
        capsule_positions[i,j] >= bone_centers[i,j] - bone_sizes[i,j] /\
        capsule_positions[i,j] <= bone_centers[i,j] + bone_sizes[i,j]
    else
        capsule_positions[i,j] = 0.0
    endif
);

% Simplified size constraints based on bone geometry
constraint forall(i in 1..n_capsules)(
    if capsule_active[i] then
        % Length constraint - must be reasonable relative to bone size
        let {
            float: max_bone_size = max([bone_sizes[i,1], bone_sizes[i,2], bone_sizes[i,3]]);
            float: min_bone_size = min([bone_sizes[i,1], bone_sizes[i,2], bone_sizes[i,3]]);
        } in (
            capsule_lengths[i] >= max_bone_size / 4.0 /\
            capsule_lengths[i] <= max_bone_size * 2.0 /\
            % Radius constraint - proportional to cross-sectional size
            capsule_radii[i] >= min_bone_size / 10.0 /\
            capsule_radii[i] <= min_bone_size / 2.0
        )
    else
        capsule_lengths[i] = 20.0 /\
        capsule_radii[i] = 10.0
    endif
);

% Minimum number of active capsules (adaptive based on available capsules)
constraint sum(i in 1..n_capsules)(capsule_active[i]) >= min(n_capsules, 1);

% No parent-child constraints - capsules use weight painting only

% Simplified overlap prevention using Manhattan distance
constraint forall(i, k in 1..n_capsules where i < k)(
    if capsule_active[i] /\ capsule_active[k] then
        let {
            var float: dx = abs(capsule_positions[i,1] - capsule_positions[k,1]);
            var float: dy = abs(capsule_positions[i,2] - capsule_positions[k,2]);
            var float: dz = abs(capsule_positions[i,3] - capsule_positions[k,3]);
            var float: manhattan_dist = dx + dy + dz;
            var float: min_separation = capsule_radii[i] + capsule_radii[k] + 0.02; % 2cm buffer
        } in
        manhattan_dist >= min_separation
    else true endif
);

% Simplified objective function components

% Size coverage: reward larger capsules
var float: size_coverage = sum(i in 1..n_capsules)(
    if capsule_active[i] then
        capsule_lengths[i] * capsule_radii[i] / 100.0  % Scale down to prevent overflow
    else 0.0 endif
);

% Bone coverage: reward capsules close to bone centers
var float: bone_coverage = sum(i in 1..n_capsules)(
    if capsule_active[i] then
        let {
            var float: dx = abs(capsule_positions[i,1] - bone_centers[i,1]);
            var float: dy = abs(capsule_positions[i,2] - bone_centers[i,2]);
            var float: dz = abs(capsule_positions[i,3] - bone_centers[i,3]);
            var float: manhattan_dist = dx + dy + dz;
            float: bone_extent = max([bone_sizes[i,1], bone_sizes[i,2], bone_sizes[i,3]]);
        } in
        if manhattan_dist <= bone_extent then 
            (bone_extent - manhattan_dist) / 10.0
        else 0.0 endif
    else 0.0 endif
);

% Overlap penalty: penalize overlapping capsules
var float: overlap_penalty_score = sum(i, k in 1..n_capsules where i < k)(
    if capsule_active[i] /\ capsule_active[k] then
        let {
            var float: dx = abs(capsule_positions[i,1] - capsule_positions[k,1]);
            var float: dy = abs(capsule_positions[i,2] - capsule_positions[k,2]);
            var float: dz = abs(capsule_positions[i,3] - capsule_positions[k,3]);
            var float: manhattan_dist = dx + dy + dz;
            var float: required_dist = capsule_radii[i] + capsule_radii[k] + 0.03; % 3cm buffer
        } in
        if manhattan_dist < required_dist then 
            (required_dist - manhattan_dist) / 10.0
        else 0.0 endif
    else 0.0 endif
);

% Count active capsules
var int: active_count = sum(i in 1..n_capsules)(capsule_active[i]);

% Simplified objective function for reliable solving
solve maximize (
    coverage_weight * (size_coverage + bone_coverage) - 
    count_penalty * active_count - 
    overlap_penalty * overlap_penalty_score
);

% Rotation swing calculation (simplified for compatibility)
array[1..n_capsules, 1..9] of var float: capsule_rotation_swing;

constraint forall(i in 1..n_capsules)(
    if capsule_active[i] then
        forall(j in 1..9)(
            capsule_rotation_swing[i,j] = bone_rotations[i,j]
        )
    else
        capsule_rotation_swing[i,1] = 1.0 /\ capsule_rotation_swing[i,2] = 0.0 /\ capsule_rotation_swing[i,3] = 0.0 /\
        capsule_rotation_swing[i,4] = 0.0 /\ capsule_rotation_swing[i,5] = 1.0 /\ capsule_rotation_swing[i,6] = 0.0 /\
        capsule_rotation_swing[i,7] = 0.0 /\ capsule_rotation_swing[i,8] = 0.0 /\ capsule_rotation_swing[i,9] = 1.0
    endif
);

% Output results in readable format
output [
    "=== VRM Triangle Mesh Capsule Optimization Results (Gecode) ===\n" ++
    "Triangle mesh data: " ++ show(n_capsules) ++ " bones from VRM analysis\n" ++
    "Fixed: Hierarchy validation, reduced complexity, overflow prevention\n" ++
    "Using float values (no scaling)\n" ++
    "Active capsules: " ++ show(fix(active_count)) ++ "/" ++ show(n_capsules) ++ "\n" ++
    "Size coverage: " ++ show(fix(size_coverage)) ++ " (scaled)\n" ++
    "Bone coverage: " ++ show(fix(bone_coverage)) ++ " (scaled)\n" ++
    "Overlap penalty: " ++ show(fix(overlap_penalty_score)) ++ "\n" ++
    "\nCapsule Results (in meters):\n"
] ++
[
    if fix(capsule_active[i]) then
        "Capsule " ++ show(i) ++ ": pos(" ++ 
        show(fix(capsule_positions[i,1])) ++ "," ++ 
        show(fix(capsule_positions[i,2])) ++ "," ++ 
        show(fix(capsule_positions[i,3])) ++ ") len(" ++
        show(fix(capsule_lengths[i])) ++ ") radii(" ++
        show(fix(capsule_radii[i])) ++ "," ++
        show(fix(capsule_radii[i])) ++ ") bone(" ++
        bone_names[i] ++ ") rot_swing(" ++
        show(fix(capsule_rotation_swing[i,1])) ++ "," ++
        show(fix(capsule_rotation_swing[i,2])) ++ "," ++
        show(fix(capsule_rotation_swing[i,3])) ++ "," ++
        show(fix(capsule_rotation_swing[i,4])) ++ "," ++
        show(fix(capsule_rotation_swing[i,5])) ++ "," ++
        show(fix(capsule_rotation_swing[i,6])) ++ "," ++
        show(fix(capsule_rotation_swing[i,7])) ++ "," ++
        show(fix(capsule_rotation_swing[i,8])) ++ "," ++
        show(fix(capsule_rotation_swing[i,9])) ++ ") dir(" ++
        show(bone_directions[i,1]) ++ "," ++
        show(bone_directions[i,2]) ++ "," ++
        show(bone_directions[i,3]) ++ ")\n"
    else ""
    endif
    | i in 1..n_capsules
] ++
["\n=== Gecode Float Optimization Complete ===\n"];
