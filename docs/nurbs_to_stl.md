# Generate STL from NURBS

Generate STL mesh files from NURBS (Non-Uniform Rational B-Spline) surface definitions.

## Usage

```bash
python nurbs_to_stl.py --shape <type> [options]
```

## Shape Options

| Shape | Description |
|-------|-------------|
| `sphere` | NURBS sphere |
| `cylinder` | NURBS cylinder |
| `cone` | NURBS cone |
| `torus` | NURBS torus |
| `box` | NURBS box (6 connected surfaces) |
| `wave` | Custom wavy surface |

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--shape`, `-s` | Shape type | sphere |
| `--output`, `-o` | Output STL file | output.stl |
| `--radius` | Radius (sphere, cylinder, cone) | 0.5 |
| `--height` | Height (cylinder, cone) | 1.0 |
| `--major-radius` | Major radius (torus) | 0.5 |
| `--minor-radius` | Minor radius (torus) | 0.15 |
| `--size` | Box dimensions (X Y Z) | 1.0 1.0 1.0 |
| `--samples` | Surface sampling resolution | 40 |

## Examples

```bash
# Generate sphere
python nurbs_to_stl.py --shape sphere --radius 0.5 -o sphere.stl

# Generate cylinder
python nurbs_to_stl.py --shape cylinder --radius 0.3 --height 2.0 -o cylinder.stl

# Generate torus
python nurbs_to_stl.py --shape torus --major-radius 0.8 --minor-radius 0.2 -o torus.stl

# Generate box
python nurbs_to_stl.py --shape box --size 2.0 1.0 0.5 -o flat_box.stl

# High resolution sphere
python nurbs_to_stl.py --shape sphere --samples 60 -o high_res_sphere.stl
```

## NURBS Parameters

### Sphere
- Degree: 2 in both U and V directions
- Control points: 5×5 grid

### Cylinder
- Degree: 2 in U, 1 in V
- Control points: 5×2 grid

### Cone  
- Degree: 2 in U, 1 in V
- Control points: 5×2 grid

### Torus
- Degree: 2 in both U and V directions
- Control points: 5×5 grid

### Box
- Degree: 1 (linear) in both directions
- 6 surfaces (one per face)

## Python API

```python
from nurbs_to_stl import (
    create_nurbs_sphere,
    create_nurbs_cylinder,
    create_nurbs_cone,
    create_nurbs_torus,
    create_nurbs_box,
    create_custom_nurbs_surface,
    nurbs_to_stl
)

# Create sphere surface
surf = create_nurbs_sphere(radius=0.5, u_samples=40, v_samples=40)

# Convert to STL
nurbs_to_stl(surf, 'output.stl')
```

## Surface Sampling

The `--samples` parameter controls mesh resolution:
- Higher values = more triangles = smoother surface
- Lower values = fewer triangles = faster computation

| Samples | Approx Triangles |
|---------|------------------|
| 20 | ~1,500 |
| 40 | ~6,000 |
| 60 | ~13,500 |
| 100 | ~37,500 |
