# Plot RCS Results

Visualize Radar Cross Section (RCS) computation results from BEM or PO computations.

## Usage

```bash
python plot_bem_rcs.py [options]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--input`, `-i` | Input .npz data file | - |
| `--output`, `-o` | Output directory | . |
| `--title` | Plot title | RCS Pattern |

## Examples

```bash
# Plot saved RCS cut
python plot_bem_rcs.py --input rcs_cut.npz --output plots/

# Plot saved 2D RCS map
python plot_bem_rcs.py --input rcs_map.npz --output plots/

# With custom title
python plot_bem_rcs.py --input rcs.npz --output plots/ --title "Delta Wing RCS"
```

## Input Format

The script reads `.npz` files containing:

```python
data = np.load('rcs.npz')
theta_deg = data['theta']      # theta values (degrees)
phi_deg = data['phi']          # phi values (degrees) - optional
rcs_db = data['rcs']          # RCS in dBsm
frequency = data['frequency']  # frequency in Hz
polarization = data['polarization']  # 'vv' or 'hh'
```

## Output

### 1D Cut Data
- `rcs_cartesian.png` - RCS vs theta (Cartesian)
- `rcs_polar.png` - RCS polar plot

### 2D Map Data
- `rcs_contour.png` - 2D theta-phi contour

### Single Point Data
- `rcs_single.png` - Bar chart for single RCS value

## Auto-Scaling

All plots use automatic scaling centered on the mean value with 50% deviation:

```
vmin = mean - mean * 0.5
vmax = mean + mean * 0.5
```

This ensures the RCS pattern is always clearly visible regardless of the absolute values.

## Plot Types

### Cartesian Plot
- X-axis: Theta (0-180°)
- Y-axis: RCS (dBsm) with auto-scaling

### Polar Plot
- Angle: Theta (0-180°)
- Radius: RCS (dBsm, relative scale)

### 2D Contour
- X-axis: Phi (0-360°)
- Y-axis: Theta (0-180°)
- Color: RCS (dBsm)

## Example Workflow

```bash
# 1. Generate mesh
python nurbs_to_stl.py --shape delta_wing -o wing.stl

# 2. Compute RCS
python bem_rcs.py wing.stl --cut --save rcs.npz

# 3. Plot results
python plot_bem_rcs.py -i rcs.npz -o plots/
```

This generates:
```
plots/
├── rcs_cartesian.png
└── rcs_polar.png
```

## Python API

```python
import numpy as np
import matplotlib.pyplot as plt
from plot_bem_rcs import (
    plot_rcs_cartesian,
    plot_rcs_polar,
    plot_rcs_2d_contour,
    auto_scale
)

# Load data
data = np.load('rcs.npz')
theta_deg = data['theta']
rcs_db = data['rcs']

# Cartesian plot
plot_rcs_cartesian(theta_deg, rcs_db, 
                   title="RCS Pattern",
                   output_path='rcs_cartesian.png')

# Polar plot  
plot_rcs_polar(theta_deg, rcs_db,
               title="RCS Pattern",
               output_path='rcs_polar.png')

# 2D contour (for map data)
phi_deg = data['phi']
rcs_map = data['rcs']
plot_rcs_2d_contour(theta_deg, phi_deg, rcs_map,
                     title="RCS Map",
                     output_path='rcs_contour.png')

# Auto-scale helper
vmin, vmax = auto_scale(rcs_db)
```

## Visualization Options

### Cartesian Plot
- Line color: Blue
- Fill: Alpha 0.3
- Grid: Enabled
- X-axis: 0-180°
- Y-axis: Auto-scaled to mean ± 50%

### Polar Plot
- Relative dB scale from mean
- Theta zero at North
- Clockwise direction

### Contour Plot
- Colormap: Jet
- Colorbar: dBsm
- Shading: Gouraud
