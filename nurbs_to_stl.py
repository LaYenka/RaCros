#!/usr/bin/env python3
"""
Generate STL files from NURBS surface definitions.
Uses geomdl library for NURBS operations.
"""

import numpy as np
from stl import mesh
import sys
import argparse
import os


def create_bezier_surface(control_points, u_samples=20, v_samples=20):
    """Create a surface mesh from Bezier control points."""
    from geomdl import BSpline
    from geomdl import utilities
    
    surf = BSpline.Surface()
    
    surf.degree_u = len(control_points) - 1
    surf.degree_v = len(control_points[0]) - 1
    
    size_u = len(control_points)
    size_v = len(control_points[0])
    
    surf.ctrlpts_size_u = size_u
    surf.ctrlpts_size_v = size_v
    
    pts = []
    for row in control_points:
        for pt in row:
            pts.append(pt)
    surf.ctrlpts = pts
    
    surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, size_u)
    surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, size_v)
    
    surf.sample_size = max(u_samples, v_samples)
    
    surf.evaluate()
    
    return surf


def nurbs_to_stl(surface, output_file: str):
    """Convert NURBS surface to STL file."""
    vertices = surface.evalpts
    sample_size = surface.sample_size
    if isinstance(sample_size, tuple):
        size_u, size_v = sample_size
    else:
        size_u = size_v = sample_size
    
    triangles = []
    for i in range(size_u - 1):
        for j in range(size_v - 1):
            idx = i * size_v + j
            
            triangles.append([idx, idx + 1, idx + size_v])
            triangles.append([idx + 1, idx + size_v + 1, idx + size_v])
    
    n_tri = len(triangles)
    
    stl_mesh = mesh.Mesh(np.zeros(n_tri, dtype=mesh.Mesh.dtype))
    
    for i, tri in enumerate(triangles):
        stl_mesh.vectors[i] = [
            vertices[tri[0]],
            vertices[tri[1]],
            vertices[tri[2]]
        ]
    
    stl_mesh.save(output_file)
    print(f"Saved: {output_file}")


def create_nurbs_sphere(radius: float = 0.5, u_samples: int = 40, v_samples: int = 40):
    """Create a NURBS sphere."""
    from geomdl import BSpline
    
    surf = BSpline.Surface()
    
    surf.degree_u = 2
    surf.degree_v = 2
    
    surf.ctrlpts_size_u = 5
    surf.ctrlpts_size_v = 5
    
    ctrlpts = []
    for i in range(5):
        row = []
        lat = np.pi * i / 4
        for j in range(5):
            lon = 2 * np.pi * j / 4
            x = radius * np.sin(lat) * np.cos(lon)
            y = radius * np.sin(lat) * np.sin(lon)
            z = radius * np.cos(lat)
            row.append([x, y, z])
        ctrlpts.append(row)
    
    flat_pts = []
    for row in ctrlpts:
        for pt in row:
            flat_pts.append(pt)
    
    surf.ctrlpts = flat_pts
    
    from geomdl import utilities
    surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, surf.ctrlpts_size_u)
    surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, surf.ctrlpts_size_v)
    
    surf.sample_size = max(u_samples, v_samples)
    surf.evaluate()
    
    return surf


def create_nurbs_cylinder(radius: float = 0.5, height: float = 1.0, 
                          u_samples: int = 40, v_samples: int = 20):
    """Create a NURBS cylinder."""
    from geomdl import BSpline
    from geomdl import utilities
    
    surf = BSpline.Surface()
    
    surf.degree_u = 2
    surf.degree_v = 1
    
    surf.ctrlpts_size_u = 5
    surf.ctrlpts_size_v = 2
    
    ctrlpts = []
    for i in range(5):
        ang = 2 * np.pi * i / 4
        x = radius * np.cos(ang)
        y = radius * np.sin(ang)
        ctrlpts.append([[x, y, -height/2], [x, y, height/2]])
    
    flat_pts = []
    for row in ctrlpts:
        for pt in row:
            flat_pts.append(pt)
    
    surf.ctrlpts = flat_pts
    
    surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, surf.ctrlpts_size_u)
    surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, surf.ctrlpts_size_v)
    
    surf.sample_size = max(u_samples, v_samples)
    surf.evaluate()
    
    return surf


def create_nurbs_cone(radius: float = 0.5, height: float = 1.0,
                      u_samples: int = 40, v_samples: int = 20):
    """Create a NURBS cone."""
    from geomdl import BSpline
    from geomdl import utilities
    
    surf = BSpline.Surface()
    
    surf.degree_u = 2
    surf.degree_v = 1
    
    surf.ctrlpts_size_u = 5
    surf.ctrlpts_size_v = 2
    
    ctrlpts = []
    for i in range(5):
        ang = 2 * np.pi * i / 4
        x = radius * np.cos(ang)
        y = radius * np.sin(ang)
        ctrlpts.append([[x, y, 0], [0, 0, height]])
    
    flat_pts = []
    for row in ctrlpts:
        for pt in row:
            flat_pts.append(pt)
    
    surf.ctrlpts = flat_pts
    
    surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, surf.ctrlpts_size_u)
    surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, surf.ctrlpts_size_v)
    
    surf.sample_size = max(u_samples, v_samples)
    surf.evaluate()
    
    return surf


def create_nurbs_torus(major_radius: float = 0.5, minor_radius: float = 0.15,
                       u_samples: int = 40, v_samples: int = 20):
    """Create a NURBS torus."""
    from geomdl import BSpline
    from geomdl import utilities
    
    surf = BSpline.Surface()
    
    surf.degree_u = 2
    surf.degree_v = 2
    
    surf.ctrlpts_size_u = 5
    surf.ctrlpts_size_v = 5
    
    ctrlpts = []
    for i in range(5):
        ang_u = 2 * np.pi * i / 4
        row = []
        for j in range(5):
            ang_v = 2 * np.pi * j / 4
            x = (major_radius + minor_radius * np.cos(ang_v)) * np.cos(ang_u)
            y = (major_radius + minor_radius * np.cos(ang_v)) * np.sin(ang_u)
            z = minor_radius * np.sin(ang_v)
            row.append([x, y, z])
        ctrlpts.append(row)
    
    flat_pts = []
    for row in ctrlpts:
        for pt in row:
            flat_pts.append(pt)
    
    surf.ctrlpts = flat_pts
    
    surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, surf.ctrlpts_size_u)
    surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, surf.ctrlpts_size_v)
    
    surf.sample_size = max(u_samples, v_samples)
    surf.evaluate()
    
    return surf


def create_nurbs_box(size: tuple = (1.0, 1.0, 1.0), 
                    u_samples: int = 10, v_samples: int = 10):
    """Create a NURBS box (6 connected surfaces)."""
    from geomdl import BSpline
    
    sx, sy, sz = size
    surfaces = []
    
    # Front face (z = sz/2)
    surf = BSpline.Surface()
    surf.degree_u = 1
    surf.degree_v = 1
    surf.ctrlpts_size_u = 2
    surf.ctrlpts_size_v = 2
    surf.ctrlpts = [
        [-sx/2, -sy/2, sz/2], [sx/2, -sy/2, sz/2],
        [-sx/2, sy/2, sz/2], [sx/2, sy/2, sz/2]
    ]
    surf.knotvector_u = [0, 0, 1, 1]
    surf.knotvector_v = [0, 0, 1, 1]
    surf.sample_size = u_samples
    surf.evaluate()
    surfaces.append(surf)
    
    # Back face (z = -sz/2)
    surf = BSpline.Surface()
    surf.degree_u = 1
    surf.degree_v = 1
    surf.ctrlpts_size_u = 2
    surf.ctrlpts_size_v = 2
    surf.ctrlpts = [
        [sx/2, -sy/2, -sz/2], [-sx/2, -sy/2, -sz/2],
        [sx/2, sy/2, -sz/2], [-sx/2, sy/2, -sz/2]
    ]
    surf.knotvector_u = [0, 0, 1, 1]
    surf.knotvector_v = [0, 0, 1, 1]
    surf.sample_size = u_samples
    surf.evaluate()
    surfaces.append(surf)
    
    # Top face (y = sy/2)
    surf = BSpline.Surface()
    surf.degree_u = 1
    surf.degree_v = 1
    surf.ctrlpts_size_u = 2
    surf.ctrlpts_size_v = 2
    surf.ctrlpts = [
        [-sx/2, sy/2, sz/2], [sx/2, sy/2, sz/2],
        [-sx/2, sy/2, -sz/2], [sx/2, sy/2, -sz/2]
    ]
    surf.knotvector_u = [0, 0, 1, 1]
    surf.knotvector_v = [0, 0, 1, 1]
    surf.sample_size = u_samples
    surf.evaluate()
    surfaces.append(surf)
    
    # Bottom face (y = -sy/2)
    surf = BSpline.Surface()
    surf.degree_u = 1
    surf.degree_v = 1
    surf.ctrlpts_size_u = 2
    surf.ctrlpts_size_v = 2
    surf.ctrlpts = [
        [-sx/2, -sy/2, -sz/2], [sx/2, -sy/2, -sz/2],
        [-sx/2, -sy/2, sz/2], [sx/2, -sy/2, sz/2]
    ]
    surf.knotvector_u = [0, 0, 1, 1]
    surf.knotvector_v = [0, 0, 1, 1]
    surf.sample_size = u_samples
    surf.evaluate()
    surfaces.append(surf)
    
    # Right face (x = sx/2)
    surf = BSpline.Surface()
    surf.degree_u = 1
    surf.degree_v = 1
    surf.ctrlpts_size_u = 2
    surf.ctrlpts_size_v = 2
    surf.ctrlpts = [
        [sx/2, -sy/2, sz/2], [sx/2, -sy/2, -sz/2],
        [sx/2, sy/2, sz/2], [sx/2, sy/2, -sz/2]
    ]
    surf.knotvector_u = [0, 0, 1, 1]
    surf.knotvector_v = [0, 0, 1, 1]
    surf.sample_size = u_samples
    surf.evaluate()
    surfaces.append(surf)
    
    # Left face (x = -sx/2)
    surf = BSpline.Surface()
    surf.degree_u = 1
    surf.degree_v = 1
    surf.ctrlpts_size_u = 2
    surf.ctrlpts_size_v = 2
    surf.ctrlpts = [
        [-sx/2, -sy/2, -sz/2], [-sx/2, -sy/2, sz/2],
        [-sx/2, sy/2, -sz/2], [-sx/2, sy/2, sz/2]
    ]
    surf.knotvector_u = [0, 0, 1, 1]
    surf.knotvector_v = [0, 0, 1, 1]
    surf.sample_size = u_samples
    surf.evaluate()
    surfaces.append(surf)
    
    return surfaces


def create_custom_nurbs_surface(degree_u: int = 2, degree_v: int = 2,
                                 ctrlpts_u: int = 5, ctrlpts_v: int = 5,
                                 scale: float = 1.0):
    """Create a custom wavy NURBS surface."""
    from geomdl import BSpline
    from geomdl import utilities
    
    surf = BSpline.Surface()
    
    surf.degree_u = degree_u
    surf.degree_v = degree_v
    
    surf.ctrlpts_size_u = ctrlpts_u
    surf.ctrlpts_size_v = ctrlpts_v
    
    ctrlpts = []
    for i in range(ctrlpts_u):
        row = []
        u = i / (ctrlpts_u - 1)
        for j in range(ctrlpts_v):
            v = j / (ctrlpts_v - 1)
            x = (u - 0.5) * 2 * scale
            y = (v - 0.5) * 2 * scale
            z = 0.1 * scale * np.sin(4 * np.pi * u) * np.sin(4 * np.pi * v)
            row.append([x, y, z])
        ctrlpts.append(row)
    
    flat_pts = []
    for row in ctrlpts:
        for pt in row:
            flat_pts.append(pt)
    
    surf.ctrlpts = flat_pts
    
    surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, surf.ctrlpts_size_u)
    surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, surf.ctrlpts_size_v)
    
    surf.sample_size = 30
    surf.evaluate()
    
    return surf


def surfaces_to_stl(surfaces, output_file: str):
    """Convert multiple NURBS surfaces to a single STL."""
    all_vertices = []
    all_faces = []
    vertex_offset = 0
    
    for surf in surfaces:
        vertices = surf.evalpts
        sample_size = surf.sample_size
        if isinstance(sample_size, tuple):
            size_u, size_v = sample_size
        else:
            size_u = size_v = sample_size
        n_verts = len(vertices)
        
        all_vertices.extend(vertices)
        
        for i in range(size_u - 1):
            for j in range(size_v - 1):
                idx = i * size_v + j
                all_faces.append([idx + vertex_offset, 
                                 idx + 1 + vertex_offset, 
                                 idx + size_v + vertex_offset])
                all_faces.append([idx + 1 + vertex_offset, 
                                 idx + size_v + 1 + vertex_offset, 
                                 idx + size_v + vertex_offset])
        
        vertex_offset += n_verts
    
    vertices = np.array(all_vertices)
    faces = np.array(all_faces)
    
    n_tri = len(faces)
    stl_mesh = mesh.Mesh(np.zeros(n_tri, dtype=mesh.Mesh.dtype))
    
    for i, tri in enumerate(faces):
        stl_mesh.vectors[i] = [
            vertices[tri[0]],
            vertices[tri[1]],
            vertices[tri[2]]
        ]
    
    stl_mesh.save(output_file)
    print(f"Saved: {output_file}")


def create_delta_wing(length: float = 2.0, span: float = 1.5, thickness: float = 0.2,
                     n_sections: int = 8):
    """Create a delta wing aircraft surface."""
    L = length
    W = span
    H = thickness
    
    sections = []
    for i in range(n_sections):
        t = i / (n_sections - 1)
        x = L/2 - t * L
        scale = 1 - t * 0.6
        h_scale = 1 - t * 0.5
        
        y_max = W/2 * scale
        z_max = H * h_scale
        
        sections.append({
            'tr': np.array([x, y_max, z_max]),
            'tl': np.array([x, -y_max, z_max]),
            'br': np.array([x, y_max, -z_max]),
            'bl': np.array([x, -y_max, -z_max]),
        })
    
    triangles = []
    
    for i in range(n_sections - 1):
        s1 = sections[i]
        s2 = sections[i + 1]
        
        triangles.append([s1['tr'], s2['tr'], s2['tl']])
        triangles.append([s1['tr'], s2['tl'], s1['tl']])
        triangles.append([s1['br'], s2['br'], s2['bl']])
        triangles.append([s1['br'], s2['bl'], s1['bl']])
        triangles.append([s1['tr'], s2['tr'], s2['br']])
        triangles.append([s1['tr'], s2['br'], s1['br']])
        triangles.append([s1['tl'], s2['tl'], s2['bl']])
        triangles.append([s1['tl'], s2['bl'], s1['bl']])
    
    sr = sections[-1]
    triangles.append([sr['tl'], sr['tr'], sr['br']])
    triangles.append([sr['tl'], sr['br'], sr['bl']])
    
    return np.array(triangles)


def delta_wing_to_stl(length: float, span: float, thickness: float,
                      n_sections: int, output_file: str):
    """Save delta wing to STL."""
    triangles = create_delta_wing(length, span, thickness, n_sections)
    
    stl_mesh = mesh.Mesh(np.zeros(len(triangles), dtype=mesh.Mesh.dtype))
    for i, tri in enumerate(triangles):
        stl_mesh.vectors[i] = tri
    
    stl_mesh.save(output_file)
    print(f"Saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Generate STL from NURBS')
    parser.add_argument('--shape', choices=['sphere', 'cylinder', 'cone', 'torus', 
                                            'box', 'wave', 'delta_wing'],
                       default='sphere', help='Shape to generate')
    parser.add_argument('--output', '-o', default='output.stl', help='Output STL file')
    parser.add_argument('--radius', type=float, default=0.5, help='Radius')
    parser.add_argument('--height', type=float, default=1.0, help='Height')
    parser.add_argument('--major-radius', type=float, default=0.5, help='Major radius (torus)')
    parser.add_argument('--minor-radius', type=float, default=0.15, help='Minor radius (torus)')
    parser.add_argument('--size', type=float, nargs=3, default=[1.0, 1.0, 1.0], help='Box dimensions')
    parser.add_argument('--samples', type=int, default=40, help='Surface samples')
    parser.add_argument('--length', type=float, default=2.0, help='Delta wing length')
    parser.add_argument('--span', type=float, default=1.5, help='Delta wing span')
    parser.add_argument('--thickness', type=float, default=0.2, help='Delta wing thickness')
    parser.add_argument('--sections', type=int, default=8, help='Number of sections')
    args = parser.parse_args()
    
    print(f"Generating {args.shape}...")
    
    if args.shape == 'sphere':
        surf = create_nurbs_sphere(args.radius, args.samples, args.samples)
        nurbs_to_stl(surf, args.output)
        
    elif args.shape == 'cylinder':
        surf = create_nurbs_cylinder(args.radius, args.height, args.samples, 20)
        nurbs_to_stl(surf, args.output)
        
    elif args.shape == 'cone':
        surf = create_nurbs_cone(args.radius, args.height, args.samples, 20)
        nurbs_to_stl(surf, args.output)
        
    elif args.shape == 'torus':
        surf = create_nurbs_torus(args.major_radius, args.minor_radius, args.samples, 20)
        nurbs_to_stl(surf, args.output)
        
    elif args.shape == 'box':
        surfaces = create_nurbs_box(tuple(args.size), 10, 10)
        surfaces_to_stl(surfaces, args.output)
        
    elif args.shape == 'wave':
        surf = create_custom_nurbs_surface(scale=1.0)
        nurbs_to_stl(surf, args.output)
        
    elif args.shape == 'delta_wing':
        delta_wing_to_stl(args.length, args.span, args.thickness, args.sections, args.output)
    
    print("Done!")


if __name__ == '__main__':
    main()
