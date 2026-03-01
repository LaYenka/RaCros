#!/usr/bin/env python3
"""Compute Radar Cross Section (RCS) from STL file using Physical Optics."""

import numpy as np
from stl import mesh
import sys
import argparse


def compute_face_properties(vertices: np.ndarray) -> tuple:
    """Compute normal, centroid, and area of a triangular face."""
    v1 = vertices[1] - vertices[0]
    v2 = vertices[2] - vertices[0]
    cross = np.cross(v1, v2)
    area = 0.5 * np.linalg.norm(cross)
    
    norm = np.linalg.norm(cross)
    if norm > 1e-10:
        normal = cross / norm
    else:
        normal = np.array([0.0, 0.0, 0.0])
    
    centroid = np.mean(vertices, axis=0)
    
    return normal, centroid, area


def spherical_to_cartesian(theta: float, phi: float) -> np.ndarray:
    """Convert spherical to Cartesian coordinates."""
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return np.array([x, y, z])


class RadarSignature:
    """Compute radar signature using Physical Optics."""
    
    def __init__(self, stl_file: str, frequency: float = 10e9):
        """Initialize with STL file and frequency."""
        self.frequency = frequency
        self.wavelength = 3e8 / frequency
        self.k = 2 * np.pi / self.wavelength
        
        self.mesh = mesh.Mesh.from_file(stl_file)
        self._precompute_properties()
    
    def _precompute_properties(self):
        """Precompute face properties."""
        n_faces = len(self.mesh.vectors)
        
        self.normals = np.zeros((n_faces, 3))
        self.centroids = np.zeros((n_faces, 3))
        self.areas = np.zeros(n_faces)
        
        for i, face in enumerate(self.mesh.vectors):
            self.normals[i], self.centroids[i], self.areas[i] = compute_face_properties(face)
    
    def compute_rcs(self, theta: float, phi: float, polarization: str = 'vv') -> float:
        """
        Compute monostatic RCS for a given angle.
        
        Args:
            theta: Elevation angle (radians)
            phi: Azimuth angle (radians)
            polarization: 'vv' or 'hh'
            
        Returns:
            RCS in m²
        """
        incident_dir = spherical_to_cartesian(theta, phi)
        
        scattered_field = np.zeros(3, dtype=complex)
        
        for i in range(len(self.mesh.vectors)):
            n = self.normals[i]
            
            if n.dot(incident_dir) <= 0:
                continue
            
            r = self.centroids[i]
            r_mag = np.linalg.norm(r)
            
            if r_mag < 1e-10:
                continue
            
            phase = self.k * r_mag
            
            h = np.cross(incident_dir, n)
            h_norm = np.linalg.norm(h)
            if h_norm > 1e-10:
                h = h / h_norm
            
            if polarization == 'vv':
                e_inc = incident_dir
            else:  # hh
                e_inc = h
            
            e_dot_n = e_inc.dot(n)
            
            factor = 1j * self.k * self.areas[i] * np.exp(1j * phase) / (2 * np.pi * r_mag)
            scattered_field += factor * n * e_dot_n
        
        rcs = 4 * np.pi * np.linalg.norm(scattered_field)**2
        
        return max(rcs, 1e-30)
    
    def compute_rcs_map(self, theta_range: np.ndarray, phi_range: np.ndarray, 
                        polarization: str = 'vv') -> np.ndarray:
        """Compute RCS over a grid of angles."""
        rcs = np.zeros((len(theta_range), len(phi_range)))
        
        for i, theta in enumerate(theta_range):
            for j, phi in enumerate(phi_range):
                rcs[i, j] = self.compute_rcs(theta, phi, polarization)
        
        return rcs
    
    def compute_rcs_cut(self, theta_range: np.ndarray, phi: float = 0.0,
                        polarization: str = 'vv') -> np.ndarray:
        """Compute RCS along theta for fixed phi."""
        return np.array([self.compute_rcs(t, phi, polarization) for t in theta_range])


def rcs_to_dbsm(rcs: np.ndarray) -> np.ndarray:
    """Convert RCS (m²) to dBsm."""
    return 10 * np.log10(np.maximum(rcs, 1e-30))


def main():
    parser = argparse.ArgumentParser(description='Compute radar signature from STL')
    parser.add_argument('stl_file', help='Path to STL file')
    parser.add_argument('--freq', type=float, default=10e9, help='Frequency in Hz (default: 10 GHz)')
    parser.add_argument('--polarization', choices=['vv', 'hh'], default='vv', help='Polarization')
    parser.add_argument('--cut', action='store_true', help='Compute theta cut (0-180 deg)')
    parser.add_argument('--map', action='store_true', help='Compute 2D theta-phi map')
    parser.add_argument('--theta-res', type=int, default=91, help='Theta resolution')
    parser.add_argument('--phi-res', type=int, default=91, help='Phi resolution')
    parser.add_argument('--theta', type=float, default=0.0, help='Theta angle in degrees')
    parser.add_argument('--phi', type=float, default=0.0, help='Phi angle in degrees')
    parser.add_argument('--save', '-s', help='Save RCS data to file (.npz)')
    args = parser.parse_args()
    
    print(f"Loading: {args.stl_file}")
    radar = RadarSignature(args.stl_file, args.freq)
    
    print(f"Frequency: {args.freq/1e9:.2f} GHz")
    print(f"Wavelength: {radar.wavelength*100:.2f} cm")
    print(f"Triangles: {len(radar.mesh.vectors)}")
    print(f"Total area: {np.sum(radar.areas):.4f} m²")
    
    if args.map:
        theta_deg = np.linspace(0, 180, args.theta_res)
        phi_deg = np.linspace(0, 360, args.phi_res)
        theta_rad = np.deg2rad(theta_deg)
        phi_rad = np.deg2rad(phi_deg)
        
        print(f"\nComputing RCS map ({args.theta_res}x{args.phi_res})...")
        
        rcs_values = radar.compute_rcs_map(theta_rad, phi_rad, args.polarization)
        rcs_db = rcs_to_dbsm(rcs_values)
        
        print(f"\nRCS Results:")
        print(f"  Max: {rcs_db.max():.2f} dBsm")
        print(f"  Min: {rcs_db.min():.2f} dBsm")
        
        if args.save:
            np.savez(args.save, 
                    theta=theta_deg, 
                    phi=phi_deg,
                    rcs=rcs_db, 
                    frequency=args.freq, 
                    polarization=args.polarization)
            print(f"Saved: {args.save}")
    elif args.cut:
        theta_deg = np.linspace(0, 180, args.theta_res)
        theta_rad = np.deg2rad(theta_deg)
        
        print(f"\nComputing RCS cut at φ={args.phi}° ({args.polarization.upper()})...")
        
        rcs_values = radar.compute_rcs_cut(theta_rad, np.deg2rad(args.phi), args.polarization)
        rcs_db = rcs_to_dbsm(rcs_values)
        
        print(f"\nRCS Results:")
        print(f"  θ=0°   (boresight): {rcs_db[0]:.2f} dBsm ({rcs_values[0]:.6e} m²)")
        print(f"  θ=90°  (broadside): {rcs_db[len(theta_deg)//2]:.2f} dBsm ({rcs_values[len(theta_deg)//2]:.6e} m²)")
        print(f"  θ=180° (back):      {rcs_db[-1]:.2f} dBsm ({rcs_values[-1]:.6e} m²)")
        
        print(f"\nMax RCS: {rcs_db.max():.2f} dBsm at θ={theta_deg[np.argmax(rcs_db)]}°")
        print(f"Min RCS: {rcs_db.min():.2f} dBsm")
        
        if args.save:
            np.savez(args.save, 
                    theta=theta_deg, 
                    rcs=rcs_db, 
                    frequency=args.freq, 
                    polarization=args.polarization)
            print(f"Saved: {args.save}")
    else:
        theta_deg = np.array([args.theta])
        theta = np.deg2rad(theta_deg)
        phi = np.deg2rad(args.phi)
        
        rcs = radar.compute_rcs(theta[0], phi, args.polarization)
        rcs_db = rcs_to_dbsm(rcs)
        
        print(f"\nRCS at θ={args.theta}°, φ={args.phi}° ({args.polarization.upper()}):")
        print(f"  {rcs_db:.2f} dBsm ({rcs:.6e} m²)")
        
        if args.save:
            np.savez(args.save, 
                    theta=theta_deg, 
                    phi=np.array([args.phi]),
                    rcs=np.array([rcs_db]), 
                    frequency=args.freq, 
                    polarization=args.polarization)
            print(f"Saved: {args.save}")


if __name__ == '__main__':
    main()
