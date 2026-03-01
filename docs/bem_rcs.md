# Compute RCS with BEM

Compute Radar Cross Section (RCS) using Boundary Element Method (BEM).

## Usage

```bash
python bem_rcs.py <stl_file> [options]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `stl_file` | Input STL file (required) | - |
| `--freq` | Frequency in Hz | 10e9 (10 GHz) |
| `--method` | BEM method (fast/full) | fast |
| `--cut` | Compute theta cut 0-180° | False |
| `--map` | Compute 2D theta-phi map | False |
| `--theta-res` | Theta resolution | 91 |
| `--phi-res` | Phi resolution | 91 |
| `--theta` | Theta angle (degrees) | 0.0 |
| `--phi` | Phi angle (degrees) | 0.0 |
| `--polarization` | Polarization (vv/hh) | vv |
| `--save`, `-s` | Save results to .npz file | - |

## Examples

```bash
# Fast BEM - single angle
python bem_rcs.py sphere.stl --freq 10e9 --theta 0

# Fast BEM - theta cut
python bem_rcs.py sphere.stl --cut --save rcs_cut.npz

# Fast BEM - 2D map
python bem_rcs.py sphere.stl --map --theta-res 91 --phi-res 91 --save rcs_map.npz

# Full BEM (Method of Moments)
python bem_rcs.py sphere.stl --method full --cut
```

## Methods

### Fast BEM
Simplified facet-based BEM using physical optics with improved phase handling. Suitable for quick estimates.

### Full BEM (MoM)
Method of Moments implementation with RWG basis functions. More accurate but computationally expensive (O(n³)).

## Output

```
Loading: sphere.stl
Frequency: 10.00 GHz
FastBEM: 1600 triangles loaded

Computing RCS cut...

RCS Results:
  θ=0°:   45.56 dBsm
  θ=90°:  45.56 dBsm
  θ=180°: 45.56 dBsm
```

## Theory

### Boundary Element Method

BEM solves the Electric Field Integral Equation (EFIE):

$$\hat{n} \times E^i = \frac{j}{k} \eta \oint J G ds$$

where:
- \(E^i\) = incident electric field
- \(J\) = induced surface current
- \(G\) = Green's function
- \(k\) = wavenumber
- \(\eta\) = intrinsic impedance

### RWG Basis Functions

The full BEM uses Rao-Wilton-Glisson (RWG) basis functions on triangular elements to represent surface currents.

### Complexity

| Method | Time Complexity | Memory |
|--------|-----------------|--------|
| Fast BEM | O(n) | O(n) |
| Full BEM | O(n³) | O(n²) |

where n = number of facets

## Save Format

Results are saved in NumPy's `.npz` format containing:

```python
np.savez('rcs.npz',
          theta=theta_deg,      # theta values in degrees
          phi=phi_deg,          # phi values in degrees (for maps)
          rcs=rcs_db,           # RCS in dBsm
          frequency=freq,       # frequency in Hz
          polarization='vv')    # polarization
```

## Python API

```python
from bem_rcs import FastBEMRCS, BEMRCS, rcs_to_dbsm

# Fast BEM
bem = FastBEMRCS('sphere.stl', frequency=10e9)

# Single angle
rcs = bem.compute_rcs(theta=0.0, phi=0.0, polarization='vv')

# Theta cut
theta_range = np.linspace(0, np.pi, 91)
rcs_values = bem.compute_rcs_cut(theta_range, phi=0.0)

# 2D Map
theta_range = np.linspace(0, np.pi, 91)
phi_range = np.linspace(0, 2*np.pi, 91)
rcs_map = bem.compute_rcs_map(theta_range, phi_range)
```

## Limitations

- Full BEM is slow for meshes with >500 triangles
- Requires significant memory for large problems
- Accuracy depends on mesh resolution relative to wavelength
