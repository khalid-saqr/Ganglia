from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from .config import Settings
from .errors import GangliaError, OperatorNotFoundError, ValidationFailure
from .openai_compat import completion_response, messages_to_user_message, model_to_operator, models_response
from .runtime import GangliaRuntime

settings = Settings.from_env()
runtime = GangliaRuntime(settings=settings)
app = FastAPI(title="Ganglia", version="1.0.0", description="Language-game reasoning-control middleware")


class ReasonRequest(BaseModel):
    message: str = Field(..., min_length=1)
    operator: str | None = "auto"
    model: str | None = None


class ReasonResponse(BaseModel):
    trace_id: str
    operator: str
    model: str
    answer: str
    controlled_reasoning: dict[str, Any]
    repair_attempts: int


def require_auth(authorization: str | None = Header(default=None)) -> None:
    if not settings.require_api_key:
        return
    if not settings.api_key:
        raise HTTPException(status_code=500, detail="GANGLIA_REQUIRE_API_KEY=true but GANGLIA_API_KEY is empty")
    expected = f"Bearer {settings.api_key}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "name": "Ganglia", "version": "1.0.0", "operators": len(runtime.registry.operators)}


@app.get("/operators")
def operators(_: None = Depends(require_auth)) -> dict[str, Any]:
    return {"operators": runtime.operators(), "invalid": runtime.registry.invalid}


@app.post("/reason", response_model=ReasonResponse)
def reason(request: ReasonRequest, _: None = Depends(require_auth)) -> dict[str, Any]:
    try:
        return runtime.reason(request.message, request.operator, request.model)
    except OperatorNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationFailure as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except GangliaError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/trace")
def list_traces(limit: int = 20, _: None = Depends(require_auth)) -> dict[str, Any]:
    if not settings.expose_trace:
        raise HTTPException(status_code=403, detail="Trace exposure disabled")
    return {"traces": runtime.trace_store.list_recent(limit)}


@app.get("/trace/{trace_id}")
def get_trace(trace_id: str, _: None = Depends(require_auth)) -> dict[str, Any]:
    if not settings.expose_trace:
        raise HTTPException(status_code=403, detail="Trace exposure disabled")
    trace = runtime.trace_store.get(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace


@app.get("/v1/models")
def v1_models(_: None = Depends(require_auth)) -> dict[str, Any]:
    return models_response([op["id"] for op in runtime.operators()])


@app.post("/v1/chat/completions")
async def v1_chat_completions(request: Request, _: None = Depends(require_auth)) -> dict[str, Any]:
    body = await request.json()
    if body.get("stream"):
        raise HTTPException(status_code=400, detail="Ganglia v1.0.0 does not support streaming responses")
    model = body.get("model") or "ganglia/auto"
    messages = body.get("messages") or []
    if not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="messages must be a list")
    user_message = messages_to_user_message(messages)
    if not user_message:
        raise HTTPException(status_code=400, detail="No usable user message found")
    operator = body.get("operator") or model_to_operator(model)
    backend_model = body.get("ganglia_model") or settings.model
    try:
        result = runtime.reason(user_message, operator, backend_model)
    except OperatorNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationFailure as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except GangliaError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return completion_response(model=model, content=result["answer"], trace_id=result["trace_id"])


def create_app() -> FastAPI:
    return app
