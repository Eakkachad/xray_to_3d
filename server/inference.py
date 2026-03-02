"""
SAX-NeRF Inference Wrapper
Wraps the original test.py logic into callable functions for the web API.
Does NOT modify any code in src/ — imports directly from the original modules.
"""

import sys
import os
import json
import time
import torch
import numpy as np
import imageio.v2 as iio
from pathlib import Path
from tqdm import tqdm

from config import settings

# Add project root to path so we can import from src/
sys.path.insert(0, str(settings.project_root))

from src.network import get_network
from src.encoder import get_encoder
from src.config.configloading import load_config
from src.render import render, run_network
from src.utils import get_psnr, get_ssim, get_psnr_3d, get_ssim_3d, cast_to_image


# ── Job tracking ──────────────────────────────────────

_jobs: dict[str, dict] = {}


def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def create_job(job_id: str, scene: str):
    _jobs[job_id] = {
        "job_id": job_id,
        "scene": scene,
        "status": "queued",
        "progress": None,
        "error": None,
    }


def update_job(job_id: str, **kwargs):
    if job_id in _jobs:
        _jobs[job_id].update(kwargs)


# ── Cache check ───────────────────────────────────────

def is_cached(scene: str) -> bool:
    """Check if inference results already exist for this scene."""
    out_dir = settings.get_scene_output_dir(scene)
    return (out_dir / "metrics.json").exists()


def get_cached_metrics(scene: str) -> dict | None:
    metrics_path = settings.get_scene_output_dir(scene) / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            return json.load(f)
    return None


def get_slice_count(scene: str, axis: str) -> int:
    """Count available slices for a given axis."""
    out_dir = settings.get_scene_output_dir(scene) / "slices" / axis
    if not out_dir.exists():
        return 0
    return len(list(out_dir.glob("*.png")))


# ── Main inference ────────────────────────────────────

def run_inference(job_id: str, scene: str):
    """
    Run SAX-NeRF inference for a given scene.
    This is called as a background task by FastAPI.
    """
    try:
        update_job(job_id, status="running", progress="Loading model...")

        config_path = str(settings.get_scene_config_path(scene))
        weights_path = str(settings.get_pretrained_path(scene))
        out_dir = settings.get_scene_output_dir(scene)

        # Validate files exist
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config not found: {config_path}")
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Weights not found: {weights_path}")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load config
        cfg = load_config(config_path)

        # Load dataset (validation split)
        update_job(job_id, progress="Loading dataset...")
        from src.dataset import TIGREDataset as Dataset
        eval_dset = Dataset(cfg["exp"]["datadir"], cfg["train"]["n_rays"], "val", device)

        # Build network
        update_job(job_id, progress="Building network...")
        network = get_network(cfg["network"]["net_type"])
        cfg["network"].pop("net_type", None)
        encoder = get_encoder(**cfg["encoder"])
        model = network(encoder, **cfg["network"]).to(device)
        model_fine = None
        n_fine = cfg["render"]["n_fine"]

        if n_fine > 0:
            model_fine = network(encoder, **cfg["network"]).to(device)

        # Load weights
        update_job(job_id, progress="Loading pretrained weights...")
        ckpt = torch.load(weights_path, map_location=device)
        model.load_state_dict(ckpt["network"])
        if n_fine > 0 and ckpt.get("network_fine"):
            model_fine.load_state_dict(ckpt["network_fine"])

        model.eval()
        if model_fine is not None:
            model_fine.eval()

        n_rays = cfg["train"]["n_rays"]
        netchunk = cfg["render"]["netchunk"]

        with torch.no_grad():
            # ── Render projections ──
            update_job(job_id, progress="Rendering projections...")
            projs = eval_dset.projs
            rays = eval_dset.rays.reshape(-1, 8)
            N, H, W = projs.shape

            projs_pred = []
            for i in range(0, rays.shape[0], n_rays):
                projs_pred.append(
                    render(rays[i:i + n_rays], model, model_fine, **cfg["render"])["acc"]
                )
            projs_pred = torch.cat(projs_pred, 0).reshape(N, H, W)

            # ── Reconstruct CT volume ──
            update_job(job_id, progress="Reconstructing 3D CT volume...")
            image = eval_dset.image
            image_pred = run_network(
                eval_dset.voxels,
                model_fine if model_fine is not None else model,
                netchunk,
            )
            image_pred = image_pred.squeeze()

            # ── Calculate metrics ──
            update_job(job_id, progress="Calculating metrics...")
            metrics = {
                "scene": scene,
                "proj_psnr": float(get_psnr(projs_pred, projs)),
                "proj_ssim": float(get_ssim(projs_pred, projs)),
                "psnr_3d": float(get_psnr_3d(image_pred, image)),
                "ssim_3d": float(get_ssim_3d(image_pred, image)),
            }

            # ── Save CT slices ──
            update_job(job_id, progress="Saving CT slices...")
            D, H_vol, W_vol = image_pred.shape

            for axis, axis_name, size in [("H", "H", D), ("W", "W", H_vol), ("L", "L", W_vol)]:
                slice_dir = out_dir / "slices" / axis_name
                slice_dir.mkdir(parents=True, exist_ok=True)
                for i in range(size):
                    if axis == "H":
                        sl = image_pred[i, ...]
                    elif axis == "W":
                        sl = image_pred[:, i, :]
                    else:
                        sl = image_pred[..., i]
                    img_np = (cast_to_image(sl) * 255).astype(np.uint8)
                    iio.imwrite(str(slice_dir / f"slice_{i:04d}.png"), img_np)

            # ── Save projection comparisons ──
            update_job(job_id, progress="Saving projections...")
            proj_dir = out_dir / "projections"
            proj_dir.mkdir(parents=True, exist_ok=True)
            n_save = min(N, 10)  # Save up to 10 projections for web display
            for i in range(n_save):
                pred_img = ((1 - cast_to_image(projs_pred[i])) * 255).astype(np.uint8)
                gt_img = ((1 - cast_to_image(projs[i])) * 255).astype(np.uint8)
                iio.imwrite(str(proj_dir / f"pred_{i:04d}.png"), pred_img)
                iio.imwrite(str(proj_dir / f"gt_{i:04d}.png"), gt_img)

            # ── Generate 3D rotating GIF ──
            update_job(job_id, progress="Generating 3D visualization...")
            _generate_gif(image_pred, out_dir)

            # ── Save metrics ──
            with open(out_dir / "metrics.json", "w") as f:
                json.dump(metrics, f, indent=2)

        # Cleanup GPU memory
        del model, model_fine, eval_dset
        torch.cuda.empty_cache()

        update_job(job_id, status="done", progress="Complete!")

    except Exception as e:
        update_job(job_id, status="error", error=str(e))
        import traceback
        traceback.print_exc()


def _generate_gif(image_pred, out_dir: Path, n_frames: int = 36):
    """Generate a rotating 3D GIF from the CT volume using matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        from skimage import measure
        import tempfile
        import shutil

        if torch.is_tensor(image_pred):
            volume = image_pred.cpu().numpy()
        else:
            volume = image_pred

        # Normalize to 0-255
        volume = ((volume - volume.min()) / (volume.max() - volume.min() + 1e-8) * 255).astype(np.uint8)

        # Find good threshold (use Otsu-like approach)
        threshold = np.percentile(volume[volume > 0], 50) if np.any(volume > 0) else 128

        try:
            verts, faces, _, _ = measure.marching_cubes(volume, level=threshold, step_size=2)
        except Exception:
            # If marching cubes fails, save a simple slice GIF instead
            _generate_slice_gif(volume, out_dir, n_frames)
            return

        if len(verts) < 3 or len(faces) < 1:
            _generate_slice_gif(volume, out_dir, n_frames)
            return

        temp_dir = tempfile.mkdtemp()
        frames = []

        for i in range(n_frames):
            angle = i * (360 / n_frames)
            fig = plt.figure(figsize=(6, 6), facecolor="black")
            ax = fig.add_subplot(111, projection="3d", facecolor="black")

            mesh = Poly3DCollection(verts[faces], alpha=0.8, edgecolor="none")
            mesh.set_facecolor([0.6, 0.7, 0.9])
            ax.add_collection3d(mesh)

            ax.set_xlim(0, verts[:, 0].max())
            ax.set_ylim(0, verts[:, 1].max())
            ax.set_zlim(0, verts[:, 2].max())
            ax.set_axis_off()
            ax.view_init(elev=20, azim=angle)

            frame_path = os.path.join(temp_dir, f"frame_{i:03d}.png")
            plt.savefig(frame_path, dpi=80, bbox_inches="tight",
                        facecolor="black", pad_inches=0)
            plt.close()
            frames.append(iio.imread(frame_path))

        gif_path = str(out_dir / "rotating_3d.gif")
        iio.mimsave(gif_path, frames, duration=0.1, loop=0)

        shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"Warning: GIF generation failed: {e}")
        # Non-critical — don't fail the whole job


def _generate_slice_gif(volume, out_dir: Path, n_frames: int = 36):
    """Fallback: generate GIF by sweeping through CT slices."""
    frames = []
    n_slices = volume.shape[0]
    step = max(1, n_slices // n_frames)

    for i in range(0, n_slices, step):
        sl = volume[i]
        if sl.ndim == 2:
            sl = np.stack([sl, sl, sl], axis=-1)
        frames.append(sl)

    if frames:
        gif_path = str(out_dir / "rotating_3d.gif")
        iio.mimsave(gif_path, frames, duration=0.15, loop=0)
