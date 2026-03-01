#!/usr/bin/env python3
"""
Boundary Element Method (Method of Moments) for Radar Cross Section computation.
Uses Electric Field Integral Equation (EFIE) for PEC surfaces.
"""

import numpy as np
from stl import mesh
import sys
from typing import Tuple, Optional
import warnings


class BEMRCS:
    """BEM-based RCS calculator using Method of Moments."""
    
    def __init__(self, stl_file: str, frequency: float = 10e9):
        """Initialize BEM RCS calculator.
        
        Args:
            stl_file: Path to STL file
            frequency: Radar frequency in Hz
        """
        self.frequency = frequency
        self.wavelength = 3e8 / frequency
        self.k = 2 * np.pi / self.wavelength
        self.eta = 377.0  # Free space impedance
        
        self.mesh = mesh.Mesh.from_file(stl_file)
        self._build_mesh()
    
    def _build_mesh(self):
        """Extract mesh geometry."""
        vectors = self.mesh.vectors
        n_tri = len(vectors)
        
        self.triangles = np.zeros((n_tri, 3, 3))
        self.centroids = np.zeros((n_tri, 3))
        self.areas = np.zeros(n_tri)
        self.normals = np.zeros((n_tri, 3))
        self.edges = []
        
        for i, tri in enumerate(vectors):
            self.triangles[i] = tri
            
            v1 = tri[1] - tri[0]
            v2 = tri[2] - tri[0]
            cross = np.cross(v1, v2)
            area = 0.5 * np.linalg.norm(cross)
            self.areas[i] = area
            
            normal = cross / np.linalg.norm(cross) if np.linalg.norm(cross) > 1e-10 else np.array([0, 0, 0])
            self.normals[i] = normal
            
            self.centroids[i] = np.mean(tri, axis=0)
            
            self.edges.append([
                (tri[0], tri[1]),
                (tri[1], tri[2]),
                (tri[2], tri[0])
            ])
        
        self.n_triangles = n_tri
        print(f"BEM: {n_tri} triangles loaded")
        print(f"Total area: {np.sum(self.areas):.4f} m²")
    
    def _compute_green_function(self, r1: np.ndarray, r2: np.ndarray) -> complex:
        """Compute Green's function G(r1, r2) = exp(-jk|r1-r2|) / (4π|r1-r2|)"""
        R = np.linalg.norm(r1 - r2)
        if R < 1e-10:
            return 0.0
        return np.exp(-1j * self.k * R) / (4 * np.pi * R)
    
    def _compute_green_derivative(self, r1: np.ndarray, r2: np.ndarray, 
                                   direction: np.ndarray) -> complex:
        """Compute derivative of Green's function."""
        R = np.linalg.norm(r1 - r2)
        if R < 1e-10:
            return 0.0
        R_vec = r1 - r2
        coeff = np.exp(-1j * self.k * R) / (4 * np.pi * R**2) * (-1j * self.k - 1/R)
        return coeff * np.dot(R_vec, direction)
    
    def _edge_basis_function(self, tri_idx: int, edge_idx: int, 
                             observation_point: np.ndarray) -> np.ndarray:
        """
        Compute RWG basis function for an edge.
        Returns a 3-component vector (Jx, Jy, Jz).
        """
        v0, v1 = self.edges[tri_idx][edge_idx]
        
        l = np.linalg.norm(v1 - v0)
        if l < 1e-10:
            return np.zeros(3)
        
        edge_center = (v0 + v1) / 2
        
        rho_plus = edge_center - v0
        rho_minus = v1 - edge_center
        
        normal_plus = self.normals[tri_idx]
        
        plus_inside = np.dot(observation_point - edge_center, normal_plus) > 0
        
        if plus_inside:
            rho = rho_plus
            area = self.areas[tri_idx]
        else:
            rho = rho_minus
            area = self.areas[tri_idx]
        
        if area < 1e-10:
            return np.zeros(3)
        
        return rho / (2 * area)
    
    def _build_impedance_matrix(self) -> np.ndarray:
        """Build impedance matrix using method of moments."""
        n = self.n_triangles * 3
        Z = np.zeros((n, n), dtype=complex)
        
        print("Building impedance matrix...")
        
        for i in range(self.n_triangles):
            if i % 200 == 0:
                print(f"  Processing triangle {i}/{self.n_triangles}")
            
            r_obs = self.centroids[i]
            n_obs = self.normals[i]
            
            for j_edge in range(3):
                j = i * 3 + j_edge
                
                J = self._edge_basis_function(i, j_edge, r_obs)
                
                integral = 0.0j
                for m in range(self.n_triangles):
                    r_source = self.centroids[m]
                    n_source = self.normals[m]
                    
                    G = self._compute_green_function(r_obs, r_source)
                    
                    dG = self._compute_green_derivative(r_obs, r_source, n_source)
                    
                    term1 = G * np.dot(J, n_source)
                    term2 = dG * np.dot(J, r_source - r_obs)
                    
                    integral += self.areas[m] * (term1 + term2)
                
                Z[i, j] = -1j * self.k * self.eta * integral
        
        print("Matrix assembly complete")
        return Z
    
    def _compute_incident_field(self, theta: float, phi: float) -> np.ndarray:
        """Compute incident electric field direction."""
        k_vec = np.array([
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        ])
        
        e_inc = np.array([0.0, 1.0, 0.0])
        
        if abs(np.dot(k_vec, e_inc)) > 0.99:
            e_inc = np.array([1.0, 0.0, 0.0])
        
        return e_inc, k_vec
    
    def _build_excitation_vector(self, theta: float, phi: float) -> np.ndarray:
        """Build excitation vector for given incident direction."""
        n = self.n_triangles * 3
        V = np.zeros(n, dtype=complex)
        
        e_inc, k_inc = self._compute_incident_field(theta, phi)
        
        for i in range(self.n_triangles):
            r = self.centroids[i]
            n_surf = self.normals[i]
            
            phase = self.k * np.dot(r, k_inc)
            
            e_inc_local = e_inc - n_surf * np.dot(e_inc, n_surf)
            
            for j_edge in range(3):
                J = self._edge_basis_function(i, j_edge, r)
                
                V[i * 3 + j_edge] = np.dot(e_inc_local, J) * np.exp(-1j * phase)
        
        return V
    
    def solve(self, theta: float, phi: float) -> np.ndarray:
        """Solve for surface currents."""
        Z = self._build_impedance_matrix()
        V = self._build_excitation_vector(theta, phi)
        
        print("Solving linear system...")
        
        try:
            J = np.linalg.solve(Z, V)
            print("Solution obtained")
            return J
        except np.linalg.LinAlgError:
            print("Using least-squares solution")
            J, _, _, _ = np.linalg.lstsq(Z, V, rcond=None)
            return J
    
    def compute_rcs(self, theta: float, phi: float, 
                    currents: Optional[np.ndarray] = None) -> float:
        """Compute RCS for given angles."""
        if currents is None:
            currents = self.solve(theta, phi)
        
        e_inc, k_inc = self._compute_incident_field(theta, phi)
        
        scattered_field = np.zeros(3, dtype=complex)
        
        for i in range(self.n_triangles):
            r = self.centroids[i]
            
            for j_edge in range(3):
                J = self._edge_basis_function(i, j_edge, r)
                idx = i * 3 + j_edge
                
                G = self._compute_green_function(np.array([0.0, 0.0, 0.0]), r)
                
                scattered_field += self.areas[i] * currents[idx] * J * np.exp(-1j * self.k * np.dot(r, k_inc))
        
        rcs = np.pi * np.linalg.norm(scattered_field)**2
        
        return max(rcs, 1e-30)
    
    def compute_rcs_cut(self, theta_range: np.ndarray, phi: float = 0.0,
                        polarization: str = 'vv') -> np.ndarray:
        """Compute RCS over theta range."""
        return np.array([self.compute_rcs(t, phi) for t in theta_range])
    
    def compute_rcs_map(self, theta_range: np.ndarray, phi_range: np.ndarray,
                        polarization: str = 'vv') -> np.ndarray:
        """Compute RCS over theta-phi grid."""
        rcs = np.zeros((len(theta_range), len(phi_range)))
        for i, theta in enumerate(theta_range):
            for j, phi in enumerate(phi_range):
                rcs[i, j] = self.compute_rcs(theta, phi)
        return rcs


class FastBEMRCS:
    """Simplified BEM for faster computation using flat facets."""
    
    def __init__(self, stl_file: str, frequency: float = 10e9):
        """Initialize Fast BEM RCS calculator."""
        self.frequency = frequency
        self.wavelength = 3e8 / frequency
        self.k = 2 * np.pi / self.wavelength
        self.eta = 377.0
        
        self.mesh = mesh.Mesh.from_file(stl_file)
        self._build_mesh()
    
    def _build_mesh(self):
        """Extract mesh geometry."""
        vectors = self.mesh.vectors
        n_tri = len(vectors)
        
        self.centroids = np.zeros((n_tri, 3))
        self.areas = np.zeros(n_tri)
        self.normals = np.zeros((n_tri, 3))
        
        for i, tri in enumerate(vectors):
            v1 = tri[1] - tri[0]
            v2 = tri[2] - tri[0]
            cross = np.cross(v1, v2)
            area = 0.5 * np.linalg.norm(cross)
            self.areas[i] = area
            
            normal = cross / np.linalg.norm(cross) if np.linalg.norm(cross) > 1e-10 else np.array([0, 0, 0])
            self.normals[i] = normal
            self.centroids[i] = np.mean(tri, axis=0)
        
        self.n_triangles = n_tri
        print(f"FastBEM: {n_tri} triangles loaded")
    
    def compute_rcs(self, theta: float, phi: float, polarization: str = 'vv') -> float:
        """Compute RCS using simplified BEM (facet-based PO)."""
        incident = np.array([
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        ])
        
        if polarization == 'vv':
            e_inc = np.array([0.0, 1.0, 0.0])
            if abs(np.dot(e_inc, incident)) > 0.99:
                e_inc = np.array([1.0, 0.0, 0.0])
        else:
            e_inc = np.cross(incident, np.array([0.0, 0.0, 1.0]))
            if np.linalg.norm(e_inc) > 1e-10:
                e_inc = e_inc / np.linalg.norm(e_inc)
            else:
                e_inc = np.array([1.0, 0.0, 0.0])
        
        scattered_field = np.zeros(3, dtype=complex)
        
        for i in range(self.n_triangles):
            n = self.normals[i]
            r = self.centroids[i]
            area = self.areas[i]
            
            dot_ni = np.dot(n, incident)
            if dot_ni <= 0:
                continue
            
            phase = 2 * self.k * np.dot(r, n)
            
            e_reflect = e_inc - 2 * dot_ni * n
            
            factor = 1j * self.k * area * np.exp(1j * phase)
            scattered_field += factor * e_reflect * dot_ni
        
        rcs = (self.wavelength**2 / (4 * np.pi)) * np.linalg.norm(scattered_field)**2
        
        return max(rcs, 1e-30)
    
    def compute_rcs_cut(self, theta_range: np.ndarray, phi: float = 0.0,
                        polarization: str = 'vv') -> np.ndarray:
        """Compute RCS over theta range."""
        return np.array([self.compute_rcs(t, phi, polarization) for t in theta_range])
    
    def compute_rcs_map(self, theta_range: np.ndarray, phi_range: np.ndarray,
                        polarization: str = 'vv') -> np.ndarray:
        """Compute RCS over theta-phi grid."""
        rcs = np.zeros((len(theta_range), len(phi_range)))
        for i, theta in enumerate(theta_range):
            for j, phi in enumerate(phi_range):
                rcs[i, j] = self.compute_rcs(theta, phi, polarization)
        return rcs


def rcs_to_dbsm(rcs) -> float:
    """Convert RCS to dBsm."""
    if isinstance(rcs, np.ndarray):
        return 10 * np.log10(np.maximum(rcs, 1e-30))
    return 10 * np.log10(max(rcs, 1e-30))


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='BEM RCS computation')
    parser.add_argument('stl_file', help='STL file path')
    parser.add_argument('--freq', type=float, default=10e9, help='Frequency in Hz')
    parser.add_argument('--method', choices=['fast', 'full'], default='fast', 
                        help='BEM method (fast=simplified, full=MoM)')
    parser.add_argument('--cut', action='store_true', help='Compute theta cut (0-180 deg)')
    parser.add_argument('--map', action='store_true', help='Compute 2D theta-phi map')
    parser.add_argument('--theta-res', type=int, default=91, help='Theta resolution')
    parser.add_argument('--phi-res', type=int, default=91, help='Phi resolution')
    parser.add_argument('--theta', type=float, default=0.0, help='Theta angle (degrees)')
    parser.add_argument('--phi', type=float, default=0.0, help='Phi angle (degrees)')
    parser.add_argument('--polarization', choices=['vv', 'hh'], default='vv')
    parser.add_argument('--save', '-s', help='Save RCS data to file (.npz)')
    args = parser.parse_args()
    
    print(f"Loading: {args.stl_file}")
    print(f"Frequency: {args.freq/1e9:.2f} GHz")
    
    if args.method == 'fast':
        bem = FastBEMRCS(args.stl_file, args.freq)
    else:
        bem = BEMRCS(args.stl_file, args.freq)
    
    if args.map:
        theta_deg = np.linspace(0, 180, args.theta_res)
        phi_deg = np.linspace(0, 360, args.phi_res)
        theta_rad = np.deg2rad(theta_deg)
        phi_rad = np.deg2rad(phi_deg)
        
        print(f"\nComputing RCS map ({args.theta_res}x{args.phi_res})...")
        rcs_values = bem.compute_rcs_map(theta_rad, phi_rad, args.polarization)
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
        theta_deg = np.linspace(0, 180, 181)
        theta_rad = np.deg2rad(theta_deg)
        
        print(f"\nComputing RCS cut...")
        rcs_values = bem.compute_rcs_cut(theta_rad, np.deg2rad(args.phi), args.polarization)
        rcs_db = rcs_to_dbsm(rcs_values)
        
        print(f"\nRCS Results:")
        print(f"  θ=0°:   {rcs_db[0]:.2f} dBsm")
        print(f"  θ=90°:  {rcs_db[90]:.2f} dBsm")
        print(f"  θ=180°: {rcs_db[180]:.2f} dBsm")
        
        if args.save:
            np.savez(args.save, theta=theta_deg, rcs=rcs_db, 
                    frequency=args.freq, polarization=args.polarization)
            print(f"Saved: {args.save}")
    else:
        theta_deg = np.array([args.theta])
        theta = np.deg2rad(theta_deg)
        phi = np.deg2rad(args.phi)
        
        rcs = bem.compute_rcs(theta[0], phi, args.polarization)
        rcs_db = rcs_to_dbsm(rcs)
        
        print(f"\nRCS at θ={args.theta}°, φ={args.phi}°: {rcs_db:.2f} dBsm")
        
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
