# RCS Radar Signature - Quick Start Guide

Generate STL meshes and compute Radar Cross Section (RCS) patterns.

## Installation

```bash
pip install numpy matplotlib stl geomdl
```

## Complete Workflow

### Step 1: Generate STL Mesh

```bash
# Generate different shapes
python nurbs_to_stl.py --shape sphere --output sphere.stl
python nurbs_to_stl.py --shape cylinder --output cylinder.stl
python nurbs_to_stl.py --shape cone --output cone.stl
python nurbs_to_stl.py --shape torus --output torus.stl
python nurbs_to_stl.py --shape box --output box.stl

# Custom parameters
python nurbs_to_stl.py --shape sphere --radius 0.5 --samples 40 --output sphere.stl
python nurbs_to_stl.py --shape torus --major-radius 0.8 --minor-radius 0.2 --output torus.stl
```

### Step 2: View STL Mesh

```bash
python plot_stl.py sphere.stl sphere_plot.png
python read_stl.py sphere.stl
```

### Step 3: Compute RCS

```bash
# Single angle
python bem_rcs.py sphere.stl --save single.npz

# Theta cut (0-180 degrees)
python bem_rcs.py sphere.stl --cut --save cut.npz

# 2D theta-phi map
python bem_rcs.py sphere.stl --map --theta-res 91 --phi-res 91 --save map.npz
```

### Step 4: Plot Results

```bash
# Plot saved RCS data
python plot_rcs.py --input cut.npz --output plots/
python plot_rcs.py --input map.npz --output plots/
python plot_rcs.py --input single.npz --output plots/
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `nurbs_to_stl.py` | Generate STL from NURBS shapes |
| `plot_stl.py` | Visualize STL mesh |
| `read_stl.py` | Show STL info (triangles, area) |
| `bem_rcs.py` | Compute RCS (fast BEM) |
| `compute_rcs.py` | Compute RCS (Physical Optics) |
| `plot_rcs.py` | Plot RCS results |

## Examples

### Sphere RCS

```bash
# 1. Generate mesh
python nurbs_to_stl.py --shape sphere --radius 0.5 --samples 40 -o sphere.stl

# 2. View mesh
python plot_stl.py sphere.stl sphere.png

# 3. Compute RCS cut
python bem_rcs.py sphere.stl --cut --save rcs.npz

# 4. Plot
python plot_rcs.py --input rcs.npz --output plots/
```

### Full 2D Map

```bash
python bem_rcs.py sphere.stl --map --theta-res 91 --phi-res 91 --save rcs_map.npz
python plot_rcs.py --input rcs_map.npz --output plots/
```

### Delta Wing

```bash
python nurbs_to_stl.py --shape delta_wing -o wing.stl
python bem_rcs.py wing.stl --cut --save rcs.npz
python plot_rcs.py --input rcs.npz --output plots/
```

## Output Files

| File | Description |
|------|-------------|
| `stl_*.stl` | Generated mesh |
| `*_plot.png` | STL visualization |
| `*.npz` | RCS data |
| `rcs_cartesian.png` | RCS vs theta |
| `rcs_polar.png` | Polar plot |
| `rcs_contour.png` | 2D contour map |
| `rcs_single.png` | Single point |

## Arguments

### nurbs_to_stl.py
```
--shape [sphere|cylinder|cone|torus|box|wave|delta_wing]
--length L           # delta wing length (default 2.0)
--span S             # delta wing span (default 1.5)
--thickness T        # delta wing thickness (default 0.2)
--sections N         # number of sections (default 8)
--radius R           # radius (default 0.5)
--height H           # height (default 1.0)
--samples N          # resolution (default 40)
--output FILE        # output STL
```

### bem_rcs.py
```
stl_file             # input STL
--cut                # compute theta cut
--map                # compute 2D map
--freq F             # frequency in Hz (default 10e9)
--theta-res N        # theta resolution
--phi-res N          # phi resolution
--save FILE          # save to .npz
```

### plot_rcs.py
```
--input FILE         # input .npz
--output DIR         # output directory
--title TEXT         # plot title
```
