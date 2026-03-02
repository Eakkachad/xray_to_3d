"""
SAX-NeRF Web API
FastAPI backend for serving pretrained model inference results.
"""

import uuid
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from schemas import (
    ScenesResponse, SceneInfo,
    InferenceResponse, JobStatusResponse, MetricsResponse, SliceInfo,
    JobStatus,
)
from inference import (
    run_inference, is_cached, get_cached_metrics,
    get_slice_count, create_job, get_job, update_job,
)


# ── App lifecycle ─────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events."""
    print(f"SAX-NeRF Web API starting on {settings.api_host}:{settings.api_port}")
    print(f"Project root: {settings.project_root}")
    print(f"Available scenes: {len(settings.get_available_scenes())}")
    yield
    print("SAX-NeRF Web API shutting down")


app = FastAPI(
    title="SAX-NeRF Web API",
    description="API for sparse-view X-ray 3D reconstruction using pretrained SAX-NeRF models",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── API Endpoints ─────────────────────────────────────

@app.get("/api/scenes", response_model=ScenesResponse)
async def list_scenes():
    """List all available scenes with their readiness status."""
    scenes = settings.get_available_scenes()
    return ScenesResponse(
        scenes=[SceneInfo(**s) for s in scenes],
        total=len(scenes),
    )


@app.post("/api/inference/{scene}", response_model=InferenceResponse)
async def start_inference(scene: str, background_tasks: BackgroundTasks):
    """Start inference for a given scene. Returns immediately with a job ID."""
    # Validate scene exists
    available = {s["name"] for s in settings.get_available_scenes()}
    if scene not in available:
        raise HTTPException(404, f"Scene '{scene}' not found")

    # Check if data/weights are ready
    scene_info = next(s for s in settings.get_available_scenes() if s["name"] == scene)
    if not scene_info["ready"]:
        missing = []
        if not scene_info["data_ready"]:
            missing.append(f"data/{scene}_50.pickle")
        if not scene_info["pretrained_ready"]:
            missing.append(f"pretrained/{scene}.tar")
        raise HTTPException(
            400,
            f"Scene '{scene}' is not ready. Missing: {', '.join(missing)}"
        )

    # Check cache
    if is_cached(scene):
        return InferenceResponse(
            job_id="cached",
            scene=scene,
            status=JobStatus.DONE,
            message="Results loaded from cache",
        )

    # Create job and run in background
    job_id = str(uuid.uuid4())[:8]
    create_job(job_id, scene)
    background_tasks.add_task(run_inference, job_id, scene)

    return InferenceResponse(
        job_id=job_id,
        scene=scene,
        status=JobStatus.QUEUED,
        message="Inference job queued",
    )


@app.get("/api/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Check the status of an inference job."""
    if job_id == "cached":
        return JobStatusResponse(
            job_id="cached", scene="", status=JobStatus.DONE, progress="Loaded from cache"
        )

    job = get_job(job_id)
    if job is None:
        raise HTTPException(404, f"Job '{job_id}' not found")

    return JobStatusResponse(**job)


@app.get("/api/results/{scene}/metrics", response_model=MetricsResponse)
async def get_metrics(scene: str):
    """Get evaluation metrics for a completed inference."""
    metrics = get_cached_metrics(scene)
    if metrics is None:
        raise HTTPException(404, f"No results for scene '{scene}'. Run inference first.")
    return MetricsResponse(**metrics)


@app.get("/api/results/{scene}/slices/{axis}/info", response_model=SliceInfo)
async def get_slice_info(scene: str, axis: str):
    """Get info about available slices for an axis (H, W, or L)."""
    if axis not in ("H", "W", "L"):
        raise HTTPException(400, "Axis must be H, W, or L")
    count = get_slice_count(scene, axis)
    if count == 0:
        raise HTTPException(404, f"No slices for scene '{scene}' axis '{axis}'")
    return SliceInfo(scene=scene, axis=axis, total_slices=count)


@app.get("/api/results/{scene}/slices/{axis}/{index}")
async def get_slice_image(scene: str, axis: str, index: int):
    """Get a single CT slice image as PNG."""
    if axis not in ("H", "W", "L"):
        raise HTTPException(400, "Axis must be H, W, or L")

    slice_path = settings.get_scene_output_dir(scene) / "slices" / axis / f"slice_{index:04d}.png"
    if not slice_path.exists():
        raise HTTPException(404, f"Slice not found: {axis}/{index}")
    return FileResponse(slice_path, media_type="image/png")


@app.get("/api/results/{scene}/gif")
async def get_gif(scene: str):
    """Get the 3D rotating GIF for a scene."""
    gif_path = settings.get_scene_output_dir(scene) / "rotating_3d.gif"
    if not gif_path.exists():
        raise HTTPException(404, f"GIF not found for scene '{scene}'")
    return FileResponse(gif_path, media_type="image/gif")


@app.get("/api/results/{scene}/projections/{type}/{index}")
async def get_projection(scene: str, type: str, index: int):
    """Get a projection image (pred or gt)."""
    if type not in ("pred", "gt"):
        raise HTTPException(400, "Type must be 'pred' or 'gt'")

    proj_path = settings.get_scene_output_dir(scene) / "projections" / f"{type}_{index:04d}.png"
    if not proj_path.exists():
        raise HTTPException(404, f"Projection not found: {type}/{index}")
    return FileResponse(proj_path, media_type="image/png")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    import torch
    return {
        "status": "ok",
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "scenes_available": len(settings.get_available_scenes()),
    }


# ── Run ───────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )
