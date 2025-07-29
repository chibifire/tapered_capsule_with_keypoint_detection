MEDIAPIPE TO 3D CONVERSION SYSTEM

OBJECTIVE: Convert MediaPipe 2D keypoints to 3D world coordinates with depth and scale estimation.

RESPONSIBILITY: Transform 2D screen coordinates into 3D positions suitable for capsule generation.

PROBLEM DEFINITION

MediaPipe provides 33 keypoints with 2D screen coordinates and visibility flags.

Missing depth information prevents direct 3D capsule positioning.

Scale information absent - requires external reference for absolute measurements.

Joint orientation data not directly available from 2D keypoint positions.

INPUT DATA

MediaPipe JSON with 33 keypoints per frame.

2D screen coordinates (X, Y) with visibility flags.

6000 frames of temporal motion data at 30 FPS.

Image dimensions (1024 × 1024 pixels).

OUTPUT REQUIREMENTS

3D world coordinates (X, Y, Z) for each keypoint.

Absolute scale in meters matching VRM specification.

Joint orientation vectors derived from keypoint relationships.

Confidence scores for depth estimation quality.

DEPTH ESTIMATION ALGORITHMS

Temporal correlation analysis across 6000 frames.

Motion parallax calculation from keypoint movement patterns.

Statistical depth inference using Japanese anthropometric constraints.

Silhouette analysis for limb thickness estimation.

SCALE ESTIMATION METHODS

Anthropometric proportion ratios from AIST database.

Reference object detection for absolute scale calibration.

Statistical body proportion analysis across temporal data.

Height estimation using keypoint vertical span.

TEMPORAL PROCESSING PIPELINE

Frame-by-frame keypoint extraction produces 6000 × 33 dataset.

Temporal filtering removes outlier detections.

Motion trajectory smoothing eliminates noise.

Statistical analysis calculates mean positions and variance.

VALIDATION CRITERIA

3D position accuracy within 5% of ground truth when available.

Scale estimation error less than 10% of actual dimensions.

Temporal consistency across all 6000 frames.

Joint relationship preservation from 2D to 3D conversion.

OUTPUT FORMAT

3D keypoint coordinates in VRM-compatible coordinate system.

Confidence scores for each estimated position.

Scale factor for converting to absolute measurements.

Temporal smoothness metrics for quality assessment.
