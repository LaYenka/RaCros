#!/usr/bin/env python3
"""Plot RCS results from BEM computation."""

import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys
import os


def load_rcs_data(theta_deg: np.ndarray, rcs_db: np.ndarray) -> dict:
    """Load RCS data."""
    return {'theta': theta_deg, 'rcs': rcs_db}


def auto_scale(rcs_db):
    """Calculate auto-scaling: mean ± 50% deviation."""
    mean_val = np.mean(rcs_db)
    deviation = mean_val * 0.5
    vmin = mean_val - deviation
    vmax = mean_val + deviation
    return vmin, vmax


def plot_rcs_cartesian(theta_deg: np.ndarray, rcs_db: np.ndarray, 
                       title: str = "RCS vs Theta", output_path: str = None):
    """Plot RCS in Cartesian format."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(theta_deg, rcs_db, 'b-', linewidth=2)
    ax.fill_between(theta_deg, rcs_db.min(), rcs_db, alpha=0.3)
    
    vmin, vmax = auto_scale(rcs_db)
    ax.set_ylim(vmin, vmax)
    
    ax.set_xlabel('Theta (degrees)', fontsize=12)
    ax.set_ylabel('RCS (dBsm)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 180)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close()


def plot_rcs_polar(theta_deg: np.ndarray, rcs_db: np.ndarray,
                   title: str = "RCS Polar Plot", output_path: str = None):
    """Plot RCS in polar format."""
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    
    theta_rad = np.deg2rad(theta_deg)
    
    vmin, vmax = auto_scale(rcs_db)
    
    r_db = rcs_db.copy()
    r_db_plot = r_db - vmin
    
    ax.plot(theta_rad, r_db_plot, 'b-', linewidth=2)
    ax.fill(theta_rad, r_db_plot, alpha=0.3, color='blue')
    
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_title(title, pad=20)
    
    n_ticks = 5
    yticks = np.linspace(0, vmax - vmin, n_ticks)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{int(vmin + y)}' for y in yticks])
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close()


def plot_rcs_2d_contour(theta_deg: np.ndarray, phi_deg: np.ndarray,
                         rcs_matrix: np.ndarray, title: str = "RCS 2D Contour",
                         output_path: str = None):
    """Plot RCS as 2D contour."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    Theta, Phi = np.meshgrid(np.deg2rad(theta_deg), np.deg2rad(phi_deg))
    
    if rcs_matrix.shape[0] == len(phi_deg) and rcs_matrix.shape[1] == len(theta_deg):
        rcs_plot = rcs_matrix.T
    else:
        rcs_plot = rcs_matrix
    
    vmin, vmax = auto_scale(rcs_plot)
    
    im = ax.pcolormesh(np.deg2rad(phi_deg), np.deg2rad(theta_deg), rcs_plot,
                       shading='gouraud', cmap='jet', vmin=vmin, vmax=vmax)
    
    ax.set_xlabel('Phi (degrees)', fontsize=12)
    ax.set_ylabel('Theta (degrees)', fontsize=12)
    ax.set_title(title, fontsize=14)
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('RCS (dBsm)', fontsize=12)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close()


def generate_test_data(method: str = 'po', n_theta: int = 181) -> tuple:
    """Generate test RCS data for demonstration."""
    theta_deg = np.linspace(0, 180, n_theta)
    
    if method == 'po' or method == 'bem':
        rcs_db = -10 + 50 * np.exp(-((theta_deg - 90) ** 2) / 500)
    elif method == 'sphere':
        rcs_db = -1.05 * np.ones_like(theta_deg)
    else:
        rcs_db = 20 + 20 * np.sin(np.deg2rad(theta_deg)) ** 2
    
    return theta_deg, rcs_db


def main():
    parser = argparse.ArgumentParser(description='Plot RCS from BEM computation')
    parser.add_argument('--input', '-i', help='Input data file (npz format)')
    parser.add_argument('--output', '-o', default='.', help='Output directory')
    parser.add_argument('--title', default='RCS Pattern', help='Plot title')
    parser.add_argument('--method', choices=['po', 'bem', 'sphere', 'test'], 
                       default='test', help='Generate test data')
    parser.add_argument('--n-theta', type=int, default=181, help='Number of theta points')
    parser.add_argument('--type', choices=['cut', 'map', 'auto'], default='auto', help='Plot type')
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    if args.input and os.path.exists(args.input):
        print(f"Loading data from: {args.input}")
        data = np.load(args.input)
        theta_deg = data['theta']
        rcs_db = data['rcs']
        
        if 'phi' in data:
            phi_deg = data['phi']
            plot_type = 'map'
        else:
            phi_deg = None
            plot_type = 'cut'
    else:
        print(f"Generating {args.method} test data...")
        theta_deg, rcs_db = generate_test_data(args.method, args.n_theta)
    
    base_title = args.title
    
    print("Generating plots...")
    
    if len(rcs_db) == 1:
        print(f"\n=== Single Point RCS ===")
        print(f"Theta: {theta_deg[0]:.1f}°")
        print(f"RCS: {rcs_db[0]:.2f} dBsm")
        
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar([theta_deg[0]], [rcs_db[0]], color='steelblue', width=5)
        ax.set_xlabel('Theta (degrees)')
        ax.set_ylabel('RCS (dBsm)')
        ax.set_title(f'{base_title} - Single Point')
        ax.set_xlim(-10, 10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(args.output, 'rcs_single.png'), dpi=150, bbox_inches='tight')
        print(f"Saved: rcs_single.png")
        plt.close()
    elif len(rcs_db.shape) == 2:
        plot_rcs_2d_contour(
            theta_deg, phi_deg, rcs_db,
            title=f"{base_title} - 2D Contour",
            output_path=os.path.join(args.output, 'rcs_contour.png')
        )
    else:
        plot_rcs_cartesian(
            theta_deg, rcs_db,
            title=f"{base_title} - Cartesian",
            output_path=os.path.join(args.output, 'rcs_cartesian.png')
        )
        
        plot_rcs_polar(
            theta_deg, rcs_db,
            title=f"{base_title} - Polar",
            output_path=os.path.join(args.output, 'rcs_polar.png')
        )
    
    print("Done!")


if __name__ == '__main__':
    main()
