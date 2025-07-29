#!/bin/bash

# Run all shape-related tests
echo "Running All Shape Tests"
echo "======================"

# Create output directory
mkdir -p output/shapes

# Run individual tests
echo "1. Testing basic shape generation..."
python3 test_shapes.py

echo -e "\n2. Testing CoACD compatibility..."
python3 test_coacd_compatible_shapes.py

echo -e "\n3. Testing shapes with CoACD..."
python3 test_shapes_coacd.py

echo -e "\n4. Testing GLB files..."
python3 test_glb_files.py

echo -e "\n5. Running complete workflow test..."
python3 test_complete_workflow.py

echo -e "\nAll tests completed!"
echo "Check output/shapes directory for generated shape data."
