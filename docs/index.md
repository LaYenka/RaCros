# RCS Radar Signature Toolbox

A comprehensive Python toolbox for generating STL meshes from NURBS surfaces and computing Radar Cross Section (RCS) using Physical Optics and Boundary Element Methods.

## Features

- **STL File Handling**: Read, visualize, and generate STL mesh files
- **NURBS Support**: Create STL meshes from NURBS surface definitions (sphere, cylinder, cone, torus, box, custom)
- **RCS Computation**: 
  - Physical Optics (PO) method
  - Fast BEM (simplified facet-based)
  - Full BEM Method of Moments (MoM)
- **Visualization**: Plot RCS patterns in Cartesian, polar, and 2D contour formats

## Installation

```bash
pip install numpy matplotlib stl geomdl
```

## Quick Start

```bash
# Generate a sphere STL
python nurbs_to_stl.py --shape sphere --output sphere.stl

# Compute RCS
python bem_rcs.py sphere.stl --cut --save rcs_data.npz

# Plot results
python plot_bem_rcs.py --input rcs_data.npz --output plots/
```

## Available Scripts

| Script | Description |
|--------|-------------|
| `read_stl.py` | Read and display STL file information |
| `plot_stl.py` | Visualize STL mesh in 3D |
| `nurbs_to_stl.py` | Generate STL from NURBS definitions |
| `compute_rcs.py` | Compute RCS using Physical Optics |
| `bem_rcs.py` | Compute RCS using BEM methods |
| `plot_bem_rcs.py` | Plot RCS results |

## Directory Structure

```
/opt/dev/Qiskit/
├── read_stl.py          # STL reader
├── plot_stl.py          # STL visualizer  
├── nurbs_to_stl.py      # NURBS to STL converter
├── compute_rcs.py       # PO RCS calculator
├── bem_rcs.py           # BEM RCS calculator
├── plot_bem_rcs.py      # RCS plotter
├── mkdocs.yml           # Documentation config
└── docs/                # Documentation files
```

## Theoretical Background

### Radar Cross Section

Radar Cross Section (RCS) measures how detectable an object is by radar. It's measured in square meters (m²) or decibels relative to a square meter (dBsm):

$$\sigma_{dBsm} = 10 \log_{10}(\sigma_{m^2})$$

### Physical Optics (PO)

PO is a high-frequency approximation that assumes currents on illuminated surfaces are twice the incident magnetic field. It's fast but less accurate for complex shapes.

### Boundary Element Method (BEM)

BEM (Method of Moments) solves integral equations for surface currents. More accurate than PO but computationally expensive (O(n³) complexity).

## Examples

### Generate and Compute RCS for a Sphere

```bash
# Generate sphere mesh
python nurbs_to_stl.py --shape sphere --radius 0.5 --samples 40 -o sphere.stl

# View mesh
python plot_stl.py sphere.stl sphere_plot.png

# Compute RCS cut
python bem_rcs.py sphere.stl --freq 10e9 --cut -s rcs.npz

# Plot results
python plot_bem_rcs.py -i rcs.npz -o plots/
```

### Compute 2D RCS Map

```bash
python bem_rcs.py sphere.stl --map --theta-res 91 --phi-res 91 -s rcs_map.npz
python plot_bem_rcs.py -i rcs_map.npz -o plots/
```

## License

MIT License
