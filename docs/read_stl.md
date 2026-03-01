# Read STL Files

Read and display information from STL (Stereolithography) mesh files.

## Usage

```bash
python read_stl.py <stl_file>
```

## Arguments

| Argument | Description |
|----------|-------------|
| `stl_file` | Path to input STL file (required) |

## Output

The script displays:
- Number of triangles
- Total surface area (m²)
- Bounding box dimensions (X, Y, Z)
- Object dimensions

## Example

```bash
$ python read_stl.py sphere.stl

Reading: sphere.stl

Mesh Information:
  Number of triangles: 1600
  Total surface area: 3.1255 m²
  Bounding box:
    X: -0.5000 to 0.5000
    Y: -0.5000 to 0.5000
    Z: -0.5000 to 0.5000
  Dimensions:
    X: 1.0000 m
    Y: 1.0000 m
    Z: 1.0000 m
```

## Python API

```python
from stl import mesh

def read_stl(file_path: str) -> mesh.Mesh:
    """Read an STL file and return mesh object."""
    return mesh.Mesh.from_file(file_path)

def get_mesh_info(stl_mesh: mesh.Mesh) -> dict:
    """Extract information from STL mesh."""
    # Returns dict with:
    # - num_triangles
    # - bounding_box
    # - dimensions
    # - total_area
```

## STL Format

STL files describe the surface geometry of 3D objects:
- **ASCII STL**: Human-readable text format
- **Binary STL**: More compact binary format

Both formats represent surfaces as a collection of triangular facets.
