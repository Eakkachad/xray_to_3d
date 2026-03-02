from pydantic import BaseModel
from enum import Enum
from typing import Optional


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class SceneInfo(BaseModel):
    name: str
    display_name: str
    pretrained_ready: bool
    data_ready: bool
    ready: bool
    cached: bool


class ScenesResponse(BaseModel):
    scenes: list[SceneInfo]
    total: int


class InferenceRequest(BaseModel):
    scene: str


class InferenceResponse(BaseModel):
    job_id: str
    scene: str
    status: JobStatus
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    scene: str
    status: JobStatus
    progress: Optional[str] = None
    error: Optional[str] = None


class MetricsResponse(BaseModel):
    scene: str
    proj_psnr: Optional[float] = None
    proj_ssim: Optional[float] = None
    psnr_3d: Optional[float] = None
    ssim_3d: Optional[float] = None


class SliceInfo(BaseModel):
    scene: str
    axis: str
    total_slices: int
