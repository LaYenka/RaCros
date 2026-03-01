#!/usr/bin/env python3
"""Plot 3D STL mesh."""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from stl import mesh
import sys


def plot_stl(file_path: str, output_path: str = None):
    """Plot STL mesh in 3D."""
    stl_mesh = mesh.Mesh.from_file(file_path)
    
    vectors = stl_mesh.vectors
    n_triangles = len(vectors)
    vertices = vectors.reshape(-1, 3)
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    triangles = np.arange(n_triangles * 3).reshape(n_triangles, 3)
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.plot_trisurf(x, y, z, triangles=triangles, 
                    alpha=0.7, color='steelblue', edgecolor='gray', linewidth=0.1)
    
    mid_x = (x.max() + x.min()) / 2
    mid_y = (y.max() + y.min()) / 2
    mid_z = (z.max() + z.min()) / 2
    
    max_range = max(x.max()-x.min(), y.max()-y.min(), z.max()-z.min()) / 2
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title(f'STL Mesh: {file_path}')
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()


def main():
    if len(sys.argv) < 2:
        print("Usage: python plot_stl.py <stl_file> [output_png]")
        sys.exit(1)
    
    stl_file = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    
    plot_stl(stl_file, output)


if __name__ == '__main__':
    main()
