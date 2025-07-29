#!/usr/bin/env python3
"""
GLTF Validation Script
Validates generated GLTF files to ensure they don't have the import errors that were occurring.
"""

import json
import sys
import base64
from pathlib import Path

def validate_gltf_file(gltf_path: str) -> bool:
    """Validate a GLTF file for common import errors."""
    try:
        with open(gltf_path, 'r') as f:
            gltf_data = json.load(f)
        
        print(f"Validating GLTF file: {gltf_path}")
        print("=" * 50)
        
        errors = []
        warnings = []
        
        # Check basic structure
        required_fields = ["asset", "scenes", "nodes", "meshes", "accessors", "bufferViews", "buffers"]
        for field in required_fields:
            if field not in gltf_data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            print("CRITICAL ERRORS:")
            for error in errors:
                print(f"  ❌ {error}")
            return False
        
        # Check accessor bounds (the main issue we were fixing)
        print("Checking accessor bounds...")
        for i, accessor in enumerate(gltf_data.get("accessors", [])):
            if "bufferView" in accessor:
                buffer_view_idx = accessor["bufferView"]
                if buffer_view_idx >= len(gltf_data.get("bufferViews", [])):
                    errors.append(f"Accessor {i} references invalid bufferView {buffer_view_idx}")
                else:
                    buffer_view = gltf_data["bufferViews"][buffer_view_idx]
                    buffer_idx = buffer_view.get("buffer", 0)
                    if buffer_idx >= len(gltf_data.get("buffers", [])):
                        errors.append(f"BufferView {buffer_view_idx} references invalid buffer {buffer_idx}")
                    else:
                        # Check buffer bounds
                        buffer = gltf_data["buffers"][buffer_idx]
                        byte_offset = buffer_view.get("byteOffset", 0)
                        byte_length = buffer_view.get("byteLength", 0)
                        buffer_length = buffer.get("byteLength", 0)
                        
                        if byte_offset + byte_length > buffer_length:
                            errors.append(f"BufferView {buffer_view_idx} exceeds buffer {buffer_idx} bounds")
        
        # Check skin data consistency (another major issue)
        print("Checking skin data consistency...")
        for i, skin in enumerate(gltf_data.get("skins", [])):
            joints = skin.get("joints", [])
            if "inverseBindMatrices" in skin:
                ibm_accessor_idx = skin["inverseBindMatrices"]
                if ibm_accessor_idx < len(gltf_data.get("accessors", [])):
                    ibm_accessor = gltf_data["accessors"][ibm_accessor_idx]
                    ibm_count = ibm_accessor.get("count", 0)
                    if ibm_count != len(joints):
                        errors.append(f"Skin {i}: inverse bind matrices count ({ibm_count}) != joints count ({len(joints)})")
                else:
                    errors.append(f"Skin {i} references invalid inverseBindMatrices accessor {ibm_accessor_idx}")
        
        # Check node references
        print("Checking node references...")
        for i, node in enumerate(gltf_data.get("nodes", [])):
            if "children" in node:
                for child_idx in node["children"]:
                    if child_idx >= len(gltf_data["nodes"]):
                        errors.append(f"Node {i} references invalid child {child_idx}")
        
        # Check buffer data integrity
        print("Checking buffer data integrity...")
        for i, buffer in enumerate(gltf_data.get("buffers", [])):
            if "uri" in buffer and buffer["uri"].startswith("data:"):
                # Check embedded buffer
                try:
                    uri_parts = buffer["uri"].split(",", 1)
                    if len(uri_parts) == 2:
                        encoded_data = uri_parts[1]
                        decoded_data = base64.b64decode(encoded_data)
                        actual_length = len(decoded_data)
                        declared_length = buffer.get("byteLength", 0)
                        
                        if actual_length != declared_length:
                            errors.append(f"Buffer {i}: actual length ({actual_length}) != declared length ({declared_length})")
                        else:
                            print(f"  ✅ Buffer {i}: {actual_length} bytes OK")
                except Exception as e:
                    errors.append(f"Buffer {i}: failed to decode embedded data - {e}")
            elif "uri" in buffer:
                warnings.append(f"Buffer {i} uses external URI: {buffer['uri']}")
            else:
                errors.append(f"Buffer {i} has no URI or embedded data")
        
        # Print statistics
        print("\nGLTF Statistics:")
        print(f"  Nodes: {len(gltf_data.get('nodes', []))}")
        print(f"  Meshes: {len(gltf_data.get('meshes', []))}")
        print(f"  Accessors: {len(gltf_data.get('accessors', []))}")
        print(f"  BufferViews: {len(gltf_data.get('bufferViews', []))}")
        print(f"  Buffers: {len(gltf_data.get('buffers', []))}")
        print(f"  Skins: {len(gltf_data.get('skins', []))}")
        
        # Calculate total vertices
        total_vertices = 0
        for mesh in gltf_data.get("meshes", []):
            for primitive in mesh.get("primitives", []):
                if "POSITION" in primitive.get("attributes", {}):
                    pos_accessor_idx = primitive["attributes"]["POSITION"]
                    if pos_accessor_idx < len(gltf_data["accessors"]):
                        total_vertices += gltf_data["accessors"][pos_accessor_idx].get("count", 0)
        
        print(f"  Total vertices: {total_vertices}")
        
        # Print results
        print("\nValidation Results:")
        if errors:
            print("ERRORS:")
            for error in errors:
                print(f"  ❌ {error}")
        else:
            print("  ✅ No critical errors found!")
        
        if warnings:
            print("WARNINGS:")
            for warning in warnings:
                print(f"  ⚠️  {warning}")
        
        print("=" * 50)
        return len(errors) == 0
        
    except Exception as e:
        print(f"❌ Failed to validate {gltf_path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_gltf.py <gltf_file> [additional_files...]")
        sys.exit(1)
    
    all_valid = True
    
    for gltf_file in sys.argv[1:]:
        if not Path(gltf_file).exists():
            print(f"❌ File not found: {gltf_file}")
            all_valid = False
            continue
        
        is_valid = validate_gltf_file(gltf_file)
        all_valid = all_valid and is_valid
        
        if len(sys.argv) > 2:  # Multiple files
            print()
    
    if all_valid:
        print("🎉 All GLTF files passed validation!")
        print("These files should import correctly into Godot without the previous errors.")
    else:
        print("❌ Some GLTF files failed validation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
