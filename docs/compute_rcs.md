# Compute RCS with Physical Optics

Compute Radar Cross Section (RCS) using the Physical Optics (PO) approximation.

## Usage

```bash
python compute_rcs.py <stl_file> [options]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `stl_file` | Input STL file (required) | - |
| `--freq` | Frequency in Hz | 10e9 (10 GHz) |
| `--polarization` | Polarization (vv/hh) | vv |
| `--theta` | Theta angle (degrees) | 0.0 |
| `--phi` | Phi angle (degrees) | 0.0 |
| `--cut` | Compute theta cut 0-180° | False |

## Examples

```bash
# Single angle
python compute_rcs.py sphere.stl --freq 10e9 --theta 45 --phi 30

# Theta cut (0-180 degrees)
python compute_rcs.py sphere.stl --cut

# Different polarization
python compute_rcs.py sphere.stl --cut --polarization hh
```

## Output

```
Loading: sphere.stl
Frequency: 10.00 GHz
Wavelength: 3.00 cm
Triangles: 1600
Total area: 3.1255 m²

Computing RCS cut at φ=0.0° (VV)...

RCS Results:
  θ=0°   (boresight): 41.80 dBsm
  θ=90°  (broadside): 41.84 dBsm
  θ=180° (back):      41.80 dBsm
```

## Physical Optics Theory

Physical Optics (PO) is a high-frequency asymptotic method that approximates the surface currents on an illuminated object:

$$J = 2 \hat{n} \times H_i$$

where:
- \(J\) = induced surface current
- \(\hat{n}\) = surface normal
- \(H_i\) = incident magnetic field

The scattered field is computed by integrating the induced currents over the surface.

### Advantages
- Fast computation (O(n) where n = number of facets)
- Works well for smooth, large objects relative to wavelength

### Limitations
- Less accurate for shadowed regions
- Poor for thin structures or edges
- Not valid for resonant-sized objects

## Python API

```python
from compute_rcs import RadarSignature, rcs_to_dbsm

# Initialize
radar = RadarSignature('sphere.stl', frequency=10e9)

# Single angle RCS
rcs = radar.compute_rcs(theta=np.pi/4, phi=np.pi/6, polarization='vv')

# Convert to dBsm
rcs_db = rcs_to_dbsm(rcs)

# Theta cut
theta_range = np.linspace(0, np.pi, 181)
rcs_values = radar.compute_rcs_cut(theta_range, phi=0.0)
```

## RCS Units

- **Linear**: square meters (m²)
- **Decibels relative to 1 m²**: dBsm

$$RCS_{dBsm} = 10 \log_{10}(RCS_{m^2})$$

### Reference Values

| Object | RCS (m²) | RCS (dBsm) |
|--------|----------|------------|
| Sphere (r=0.5m) | 0.785 | -1.05 |
| Plate (1m×1m) | 1.0 | 0.0 |
| Car | 10-100 | 10-20 |
| Fighter jet | 0.1-5 | -10 to 7 |
