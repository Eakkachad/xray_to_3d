import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from skimage import measure
import imageio.v2 as iio
import os
from pathlib import Path

def load_ct_volume(ct_dir):
    """Load all CT slices and stack into 3D volume"""
    files = sorted(Path(ct_dir).glob("ct_pred_*.png"), 
                   key=lambda x: int(x.stem.split('_')[-1]))
    
    print(f"Loading {len(files)} CT slices...")
    slices = [iio.imread(f) for f in files]
    volume = np.stack(slices, axis=0)
    print(f"Volume shape: {volume.shape}")
    return volume

def create_3d_surface(volume, threshold=128, step_size=2):
    """Create 3D surface mesh from volume using marching cubes"""
    print(f"Generating 3D surface (threshold={threshold})...")
    
    # Use marching cubes to find surface
    verts, faces, normals, values = measure.marching_cubes(
        volume, level=threshold, step_size=step_size
    )
    
    print(f"Generated {len(verts)} vertices, {len(faces)} faces")
    return verts, faces, normals

def plot_3d_mesh(verts, faces, output_path, title="3D Jaw Reconstruction"):
    """Plot 3D mesh and save"""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create mesh
    mesh = Poly3DCollection(verts[faces], alpha=0.7, edgecolor='none')
    mesh.set_facecolor([0.8, 0.8, 0.9])
    ax.add_collection3d(mesh)
    
    # Set limits
    ax.set_xlim(0, verts[:, 0].max())
    ax.set_ylim(0, verts[:, 1].max())
    ax.set_zlim(0, verts[:, 2].max())
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title, fontsize=16, fontweight='bold')
    
    # Set viewing angle
    ax.view_init(elev=20, azim=45)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved 3D visualization to: {output_path}")
    plt.close()

def create_multiple_views(verts, faces, output_dir):
    """Create multiple viewing angles"""
    views = [
        (20, 45, 'view_default.png'),
        (20, 0, 'view_front.png'),
        (20, 90, 'view_side.png'),
        (90, 0, 'view_top.png'),
    ]
    
    os.makedirs(output_dir, exist_ok=True)
    
    for elev, azim, filename in views:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        mesh = Poly3DCollection(verts[faces], alpha=0.8, edgecolor='none')
        mesh.set_facecolor([0.85, 0.85, 0.95])
        ax.add_collection3d(mesh)
        
        ax.set_xlim(0, verts[:, 0].max())
        ax.set_ylim(0, verts[:, 1].max())
        ax.set_zlim(0, verts[:, 2].max())
        
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.set_zlabel('Z', fontsize=12)
        
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(f'Jaw 3D ({filename.split(".")[0]})', fontsize=14)
        
        output_path = os.path.join(output_dir, filename)
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Saved: {output_path}")
        plt.close()

def create_rotating_gif(verts, faces, output_path, frames=36):
    """Create rotating GIF animation"""
    import tempfile
    
    print(f"Creating rotating animation ({frames} frames)...")
    temp_dir = tempfile.mkdtemp()
    
    for i in range(frames):
        angle = i * (360 / frames)
        
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        mesh = Poly3DCollection(verts[faces], alpha=0.8, edgecolor='none')
        mesh.set_facecolor([0.85, 0.85, 0.95])
        ax.add_collection3d(mesh)
        
        ax.set_xlim(0, verts[:, 0].max())
        ax.set_ylim(0, verts[:, 1].max())
        ax.set_zlim(0, verts[:, 2].max())
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'3D Jaw Reconstruction', fontsize=14, fontweight='bold')
        
        ax.view_init(elev=20, azim=angle)
        
        frame_path = os.path.join(temp_dir, f'frame_{i:03d}.png')
        plt.savefig(frame_path, dpi=100, bbox_inches='tight', facecolor='white')
        plt.close()
    
    # Create GIF
    images = []
    for i in range(frames):
        frame_path = os.path.join(temp_dir, f'frame_{i:03d}.png')
        images.append(iio.imread(frame_path))
    
    iio.mimsave(output_path, images, duration=0.1, loop=0)
    print(f"Saved rotating GIF to: {output_path}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    # Paths
    ct_dir = "output/Lineformer/jaw/CT/H/ct_pred"
    output_base = "output/Lineformer/jaw/3D_visualization"
    
    os.makedirs(output_base, exist_ok=True)
    
    print("=" * 60)
    print("SAX-NeRF 3D Visualization")
    print("=" * 60)
    
    # Load volume
    volume = load_ct_volume(ct_dir)
    
    # Create 3D surface
    verts, faces, normals = create_3d_surface(volume, threshold=128, step_size=2)
    
    # Create visualizations
    print("\n" + "=" * 60)
    print("Creating 3D visualizations...")
    print("=" * 60)
    
    # Single view
    plot_3d_mesh(verts, faces, 
                 os.path.join(output_base, "jaw_3d_main.png"),
                 "SAX-NeRF: 3D Jaw Reconstruction")
    
    # Multiple views
    create_multiple_views(verts, faces, 
                         os.path.join(output_base, "views"))
    
    # Rotating GIF
    create_rotating_gif(verts, faces,
                       os.path.join(output_base, "jaw_3d_rotating.gif"),
                       frames=36)
    
    print("\n" + "=" * 60)
    print("✓ 3D Visualization Complete!")
    print("=" * 60)
    print(f"Output directory: {output_base}/")
    print(f"  - jaw_3d_main.png (main view)")
    print(f"  - views/ (4 different angles)")
    print(f"  - jaw_3d_rotating.gif (animated)")
