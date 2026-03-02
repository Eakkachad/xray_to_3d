import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")


class Settings(BaseSettings):
    """Application settings — reads from .env or environment variables."""

    # GPU
    cuda_visible_devices: str = "0"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Paths
    project_root: Path = _project_root
    data_dir: Path = _project_root / "data"
    pretrained_dir: Path = _project_root / "pretrained"
    output_dir: Path = _project_root / "output"
    config_dir: Path = _project_root / "config"

    @property
    def web_cache_dir(self) -> Path:
        d = self.output_dir / "web_cache"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def get_scene_config_path(self, scene: str) -> Path:
        return self.config_dir / "Lineformer" / f"{scene}_50.yaml"

    def get_pretrained_path(self, scene: str) -> Path:
        return self.pretrained_dir / f"{scene}.tar"

    def get_data_path(self, scene: str) -> Path:
        return self.data_dir / f"{scene}_50.pickle"

    def get_scene_output_dir(self, scene: str) -> Path:
        d = self.web_cache_dir / scene
        d.mkdir(parents=True, exist_ok=True)
        return d

    def get_available_scenes(self) -> list[dict]:
        """Return list of scenes that have both config and pretrained weights."""
        scenes = []
        config_dir = self.config_dir / "Lineformer"
        if not config_dir.exists():
            return scenes

        for yaml_file in sorted(config_dir.glob("*_50.yaml")):
            scene_name = yaml_file.stem.replace("_50", "")
            pretrained_exists = self.get_pretrained_path(scene_name).exists()
            data_exists = self.get_data_path(scene_name).exists()
            cached = (self.get_scene_output_dir(scene_name) / "metrics.json").exists()
            scenes.append({
                "name": scene_name,
                "display_name": scene_name.replace("_", " ").title(),
                "pretrained_ready": pretrained_exists,
                "data_ready": data_exists,
                "ready": pretrained_exists and data_exists,
                "cached": cached,
            })
        return scenes


settings = Settings()

# Set CUDA device
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = settings.cuda_visible_devices
