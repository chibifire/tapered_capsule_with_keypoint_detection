import struct
import json
import base64
from typing import Dict, List, Any

class GLTFParser:
    def __init__(self):
        self.gltf_data: Dict[str, Any] = {}
        self.buffers: List[bytes] = []

    def load_glb(self, file_path: str) -> bool:
        """Load binary GLTF file."""
        try:
            with open(file_path, 'rb') as file:
                # Read header
                magic = struct.unpack('4s', file.read(4))[0]
                version = struct.unpack('I', file.read(4))[0]
                length = struct.unpack('I', file.read(4))[0]
                
                # Read JSON chunk
                json_chunk_length = struct.unpack('I', file.read(4))[0]
                json_chunk_type = struct.unpack('4s', file.read(4))[0]
                self.gltf_data = json.loads(file.read(json_chunk_length).decode('utf-8'))
                
                # Read binary chunk if exists
                if file.tell() < length:
                    bin_chunk_length = struct.unpack('I', file.read(4))[0]
                    bin_chunk_type = struct.unpack('4s', file.read(4))[0]
                    bin_data = file.read(bin_chunk_length)
                    
                    # Store binary data as buffer
                    self.buffers = [bin_data]
                
                self._extract_buffers()
                return True
        except Exception as e:
            print(f"Error loading GLB file: {e}")
            return False

    def _extract_buffers(self):
        """Extract buffer data from GLTF."""
        if "buffers" in self.gltf_data and not self.buffers:
            for buffer in self.gltf_data["buffers"]:
                if "uri" in buffer:
                    if buffer["uri"].startswith("data:"):
                        # Base64 embedded data
                        data_start = buffer["uri"].find(",") + 1
                        buffer_data = base64.b64decode(buffer["uri"][data_start:])
                        self.buffers.append(buffer_data)
                    else:
                        # External file - for now just placeholder
                        self.buffers.append(b"")

    def get_accessor_data(self, accessor_idx: int) -> List:
        """Extract data from GLTF accessor."""
        if accessor_idx >= len(self.gltf_data["accessors"]):
            return []
            
        accessor = self.gltf_data["accessors"][accessor_idx]
        buffer_view = self.gltf_data["bufferViews"][accessor["bufferView"]]
        
        if buffer_view["buffer"] >= len(self.buffers):
            return []
            
        buffer_data = self.buffers[buffer_view["buffer"]]
        offset = buffer_view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        
        # Determine data format
        component_type = accessor["componentType"]
        type_str = accessor["type"]
        count = accessor["count"]
        
        # Component type mapping
        type_formats = {
            5120: 'b',   # BYTE
            5121: 'B',   # UNSIGNED_BYTE
            5122: 'h',   # SHORT
            5123: 'H',   # UNSIGNED_SHORT
            5125: 'I',   # UNSIGNED_INT
            5126: 'f'    # FLOAT
        }
        
        # Type size mapping
        type_sizes = {
            "SCALAR": 1,
            "VEC2": 2,
            "VEC3": 3,
            "VEC4": 4
        }
        
        format_char = type_formats.get(component_type, 'f')
        components = type_sizes.get(type_str, 1)
        total_elements = count * components
        
        try:
            data = struct.unpack_from(f'<{total_elements}{format_char}', buffer_data, offset)
            
            # Reshape for multi-component types
            if components > 1:
                return [list(data[i:i+components]) for i in range(0, len(data), components)]
            else:
                return list(data)
                
        except Exception as e:
            print(f"Error extracting accessor data: {e}")
            return []

    def get_gltf_data(self) -> Dict[str, Any]:
        return self.gltf_data

    def get_buffers(self) -> List[bytes]:
        return self.buffers
