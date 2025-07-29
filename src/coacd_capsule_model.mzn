% CoACD-based Tapered Capsule Optimization Model
% Solves for optimal set of tapered capsules to cover witness points

include "globals.mzn";

% Problem dimensions
int: num_capsules;
int: num_points;

% Capsule parameters (from data file)
array[1..num_capsules, 1..3] of float: capsule_centers;
array[1..num_capsules] of float: capsule_heights;
array[1..num_capsules] of float: capsule_radii_top;
array[1..num_capsules] of float: capsule_radii_bottom;
array[1..num_capsules, 1..3] of float: capsule_swing_rotations;
array[1..num_capsules] of float: capsule_twist_rotations;

% Witness points to be covered
array[1..num_points, 1..3] of float: witness_points;

% Coverage matrix (which capsules cover which points)
array[1..num_capsules, 1..num_points] of int: coverage_matrix;

% Decision variables
% Which capsules to include in the solution
array[1..num_capsules] of var bool: capsule_selected;

% Constraints
% Each witness point must be covered by at least one selected capsule
constraint forall(p in 1..num_points) (
    sum(c in 1..num_capsules)(capsule_selected[c] /\ coverage_matrix[c, p] == 1) >= 1
);

% Objective: minimize number of capsules while maximizing coverage
% We want to minimize the number of selected capsules
var int: num_selected = sum(c in 1..num_capsules)(capsule_selected[c]);

% Solve
solve minimize num_selected;

% Output
output [
    "Selected capsules: ", show(num_selected), "\n",
    "Capsule indices: [",
    join(", ", [show(c) | c in 1..num_capsules where fix(capsule_selected[c])]),
    "]\n"
] ++
[
    if fix(capsule_selected[c]) then
        "Capsule " ++ show(c) ++ 
        ": center(" ++ show(capsule_centers[c, 1]) ++ ", " ++ show(capsule_centers[c, 2]) ++ ", " ++ show(capsule_centers[c, 3]) ++
        ") height(" ++ show(capsule_heights[c]) ++
        ") radii(" ++ show(capsule_radii_top[c]) ++ ", " ++ show(capsule_radii_bottom[c]) ++
        ") swing(" ++ show(capsule_swing_rotations[c, 1]) ++ ", " ++ show(capsule_swing_rotations[c, 2]) ++ ", " ++ show(capsule_swing_rotations[c, 3]) ++
        ") twist(" ++ show(capsule_twist_rotations[c]) ++ ")\n"
    else ""
    endif
    | c in 1..num_capsules
];
