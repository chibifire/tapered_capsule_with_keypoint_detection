# Tapered Capsule Generator

A Python library and CLI tool for generating tapered capsules for glTF/GLB/VRM skinned mesh skeletons.

## Overview

This tool analyzes glTF, GLB, or VRM skinned mesh skeletons and generates optimized tapered capsule representations using constraint optimization. The capsules can be used for physics simulation, collision detection, or other applications requiring simplified representations of complex skeletal structures.

## Features

- **Multi-format Support**: Works with glTF, GLB, and VRM skinned mesh files
- **Skeleton Analysis**: Extracts bone geometry and joint hierarchy from 3D models
- **Capsule Generation**: Creates tapered capsule representations of skeletal structures
- **Constraint Optimization**: Uses MiniZinc solvers to optimize capsule parameters
- **CLI Interface**: Command-line tool for easy integration into workflows
- **Python API**: Programmable interface for custom applications

## Installation

```bash
pip install .
```

## CLI Usage

The tool provides a command-line interface with several commands:

### Analyze a model skeleton

```bash
tapered-capsule analyze model.vrm
```

### Generate capsules from a model

```bash
tapered-capsule generate model.glb --output output.gltf --max-capsules 8
```

### Generate capsules from optimization results

```bash
tapered-capsule from-results model.gltf results.txt output.gltf
```

### CLI Options

- `--max-capsules` or `-n`: Maximum number of capsules to generate (default: 8 for generate, 25 for from-results)
- `--timeout` or `-t`: Optimization timeout in seconds (default: 30)
- `--dzn`: Path to DZN data file (optional, for from-results command)
- `--version` or `-v`: Show version information

## Python API

The tool also provides a Python API for programmatic use:

```python
from tapered_capsule import SkinnedCapsulePipeline

# Analyze a model and generate capsules
pipeline = SkinnedCapsulePipeline()
pipeline.load_gltf_and_analyze("model.vrm")
pipeline.run_optimization(max_capsules=8)
pipeline.generate_gltf_output("output.gltf")
```

## Requirements

- Python 3.8+
- MiniZinc solver
- numpy
- trimesh

## License

MIT
