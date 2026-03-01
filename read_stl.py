#!/usr/bin/env python3
"""Read and display information from STL files."""

import numpy as np
from stl import mesh
import sys


def read_stl(file_path: str) -> mesh.Mesh:
    """Read an STL file and return mesh object."""
    return mesh.Mesh.from_file(file_path)


def get_mesh_info(stl_mesh: mesh.Mesh) -> dict:
    """Extract information from STL mesh."""
    vectors = stl_mesh.vectors
    
    num_triangles = len(vectors)
    
    vertices = vectors.reshape(-1, 3)
    
    x_min, x_max = vertices[:, 0].min(), vertices[:, 0].max()
    y_min, y_max = vertices[:, 1].min(), vertices[:, 1].max()
    z_min, z_max = vertices[:, 2].min(), vertices[:, 2].max()
    
    total_area = 0
    for face in vectors:
        v1 = face[1] - face[0]
        v2 = face[2] - face[0]
        cross = np.cross(v1, v2)
        total_area += 0.5 * np.linalg.norm(cross)
    
    return {
        'num_triangles': num_triangles,
        'bounding_box': {
            'x': (x_min, x_max),
            'y': (y_min, y_max),
            'z': (z_min, z_max)
        },
        'dimensions': {
            'x': x_max - x_min,
            'y': y_max - y_min,
            'z': z_max - z_min
        },
        'total_area': total_area
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python read_stl.py <stl_file>")
        sys.exit(1)
    
    stl_file = sys.argv[1]
    
    print(f"Reading: {stl_file}")
    
    stl_mesh = read_stl(stl_file)
    info = get_mesh_info(stl_mesh)
    
    print(f"\nMesh Information:")
    print(f"  Number of triangles: {info['num_triangles']}")
    print(f"  Total surface area: {info['total_area']:.4f} m²")
    print(f"  Bounding box:")
    print(f"    X: {info['bounding_box']['x'][0]:.4f} to {info['bounding_box']['x'][1]:.4f}")
    print(f"    Y: {info['bounding_box']['y'][0]:.4f} to {info['bounding_box']['y'][1]:.4f}")
    print(f"    Z: {info['bounding_box']['z'][0]:.4f} to {info['bounding_box']['z'][1]:.4f}")
    print(f"  Dimensions:")
    print(f"    X: {info['dimensions']['x']:.4f} m")
    print(f"    Y: {info['dimensions']['y']:.4f} m")
    print(f"    Z: {info['dimensions']['z']:.4f} m")


if __name__ == '__main__':
    main()
