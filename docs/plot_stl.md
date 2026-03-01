# Plot STL Files

Visualize STL (Stereolithography) mesh files in 3D.

## Usage

```bash
python plot_stl.py <stl_file> [output_png]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `stl_file` | Path to input STL file (required) |
| `output_png` | Output PNG file path (optional) |

If no output path is provided, displays interactively (requires display).

## Example

```bash
# Save to file
python plot_stl.py sphere.stl sphere_plot.png

# View mesh
python plot_stl.py sphere.stl
```

## Output

Generates a 3D visualization showing:
- Mesh surface with triangular facets
- Axis labels (X, Y, Z in meters)
- Automatic scaling to fit mesh

## Python API

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from stl import mesh

def plot_stl(file_path: str, output_path: str = None):
    """Plot STL mesh in 3D."""
    stl_mesh = mesh.Mesh.from_file(file_path)
    
    # Create figure with 3D axes
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot triangular surface
    ax.plot_trisurf(x, y, z, triangles=..., alpha=0.7)
    
    if output_path:
        fig.savefig(output_path, dpi=150)
```

## Visualization Options

The plot uses:
- **Alpha**: 0.7 (70% opacity)
- **Color**: Steel blue
- **Edge color**: Gray
- **DPI**: 150 for saved images
