from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


def _bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8717
    api_key: str = ""
    require_api_key: bool = False

    model_provider: str = "ollama"
    ollama_url: str = "http://localhost:11434"
    model: str = "llama3.1:8b"

    trace_db: str = "./ganglia_traces.sqlite"
    operators_dir: str = "./operators"
    max_retries: int = 2
    temperature: float = 0.2
    timeout_seconds: int = 120
    expose_trace: bool = False
    trace_require_api_key: bool = True

    @classmethod
    def from_env(cls, env_file: str | None = None) -> "Settings":
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        return cls(
            host=os.getenv("GANGLIA_HOST", "127.0.0.1"),
            port=int(os.getenv("GANGLIA_PORT", "8717")),
            api_key=os.getenv("GANGLIA_API_KEY", ""),
            require_api_key=_bool(os.getenv("GANGLIA_REQUIRE_API_KEY"), False),
            model_provider=os.getenv("GANGLIA_MODEL_PROVIDER", "ollama"),
            ollama_url=os.getenv("GANGLIA_OLLAMA_URL", "http://localhost:11434").rstrip("/"),
            model=os.getenv("GANGLIA_MODEL", "llama3.1:8b"),
            trace_db=os.getenv("GANGLIA_TRACE_DB", "./ganglia_traces.sqlite"),
            operators_dir=os.getenv("GANGLIA_OPERATORS_DIR", "./operators"),
            max_retries=int(os.getenv("GANGLIA_MAX_RETRIES", "2")),
            temperature=float(os.getenv("GANGLIA_TEMPERATURE", "0.2")),
            timeout_seconds=int(os.getenv("GANGLIA_TIMEOUT_SECONDS", "120")),
            expose_trace=_bool(os.getenv("GANGLIA_EXPOSE_TRACE"), False),
            trace_require_api_key=_bool(os.getenv("GANGLIA_TRACE_REQUIRE_API_KEY"), True),
        )

    @property
    def trace_db_path(self) -> Path:
        return Path(self.trace_db).expanduser().resolve()

    @property
    def operators_path(self) -> Path:
        return Path(self.operators_dir).expanduser().resolve()
