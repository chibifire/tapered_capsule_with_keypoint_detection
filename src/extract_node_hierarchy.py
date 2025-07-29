#!/usr/bin/env python3
"""
Script to extract node hierarchy information from VRM/glTF files.
"""

import sys
import json
from typing import Dict, List, Any
from gltf_parser import GLTFParser

class NodeHierarchyExtractor:
    def __init__(self):
        self.parser = GLTFParser()
        
    def load_model(self, file_path: str) -> bool:
        """Load a VRM/glTF model."""
        try:
            # Try to load as binary GLB first
            if self.parser.load_glb(file_path):
                return True
        except:
            # If that fails, try to load as JSON glTF
            try:
                with open(file_path, 'r') as f:
                    gltf_data = json.load(f)
                self.parser.gltf_data = gltf_data
                self.parser._extract_buffers()
                return True
            except Exception as e:
                print(f"Error loading model file: {e}")
                return False
        
        return False
    
    def extract_node_hierarchy(self) -> Dict[str, Any]:
        """Extract node hierarchy information from the loaded model."""
        gltf_data = self.parser.get_gltf_data()
        
        if not gltf_data or "nodes" not in gltf_data:
            return {"error": "No node data found in the model"}
        
        nodes = gltf_data["nodes"]
        scenes = gltf_data.get("scenes", [])
        
        hierarchy_info = {
            "total_nodes": len(nodes),
            "scenes": [],
            "nodes": []
        }
        
        # Extract scene information
        for i, scene in enumerate(scenes):
            scene_info = {
                "scene_index": i,
                "name": scene.get("name", f"Scene {i}"),
                "root_nodes": scene.get("nodes", [])
            }
            hierarchy_info["scenes"].append(scene_info)
        
        # Extract node information
        for i, node in enumerate(nodes):
            node_info = {
                "node_index": i,
                "name": node.get("name", f"Node {i}"),
                "children": node.get("children", []),
                "has_mesh": "mesh" in node,
                "has_camera": "camera" in node,
                "has_light": "light" in node,
                "transform": {}
            }
            
            # Extract transform information
            if "translation" in node:
                node_info["transform"]["translation"] = node["translation"]
            if "rotation" in node:
                node_info["transform"]["rotation"] = node["rotation"]
            if "scale" in node:
                node_info["transform"]["scale"] = node["scale"]
            if "matrix" in node:
                node_info["transform"]["matrix"] = node["matrix"]
            
            hierarchy_info["nodes"].append(node_info)
        
        return hierarchy_info
    
    def print_hierarchy(self, hierarchy_info: Dict[str, Any], node_index: int = 0, indent: int = 0):
        """Print the node hierarchy in a tree format."""
        if "error" in hierarchy_info:
            print(hierarchy_info["error"])
            return
            
        if node_index >= len(hierarchy_info["nodes"]):
            return
            
        node = hierarchy_info["nodes"][node_index]
        indent_str = "  " * indent
        print(f"{indent_str}- {node['name']} (index: {node['node_index']})")
        
        if node["children"]:
            for child_index in node["children"]:
                self.print_hierarchy(hierarchy_info, child_index, indent + 1)
    
    def find_root_nodes(self, hierarchy_info: Dict[str, Any]) -> List[int]:
        """Find root nodes (nodes that are not children of any other node)."""
        if "error" in hierarchy_info or not hierarchy_info["nodes"]:
            return []
            
        all_nodes = set(range(len(hierarchy_info["nodes"])))
        child_nodes = set()
        
        for node in hierarchy_info["nodes"]:
            child_nodes.update(node["children"])
            
        root_nodes = list(all_nodes - child_nodes)
        return root_nodes

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_node_hierarchy.py <vrm/gltf file> [--json]")
        print("  --json: Output in JSON format instead of tree format")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_json = "--json" in sys.argv
    
    extractor = NodeHierarchyExtractor()
    
    print(f"Loading model: {file_path}")
    if not extractor.load_model(file_path):
        print("Failed to load model")
        sys.exit(1)
    
    print("Extracting node hierarchy...")
    hierarchy_info = extractor.extract_node_hierarchy()
    
    if output_json:
        print(json.dumps(hierarchy_info, indent=2))
    else:
        print(f"\nModel Summary:")
        print(f"  Total nodes: {hierarchy_info.get('total_nodes', 0)}")
        print(f"  Scenes: {len(hierarchy_info.get('scenes', []))}")
        
        print(f"\nScene Information:")
        for scene in hierarchy_info.get('scenes', []):
            print(f"  Scene {scene['scene_index']}: {scene['name']}")
            print(f"    Root nodes: {scene['root_nodes']}")
        
        print(f"\nNode Hierarchy:")
        root_nodes = extractor.find_root_nodes(hierarchy_info)
        if root_nodes:
            for root_index in root_nodes:
                extractor.print_hierarchy(hierarchy_info, root_index, 0)
        else:
            print("  No root nodes found")

if __name__ == "__main__":
    main()
