from __future__ import annotations

from .operator_loader import OperatorRegistry


def route_operator(message: str, registry: OperatorRegistry, requested: str | None = None) -> str:
    if requested and requested not in {"", "auto", "ganglia", "ganglia/auto"}:
        if requested.startswith("ganglia/"):
            requested = requested.split("/", 1)[1]
        if registry.get(requested):
            return requested

    text = message.lower()
    best_id = "coordinate_game"
    best_score = -10_000
    for spec in registry.list():
        score = spec.routing.priority
        for hint in spec.routing.intent_hints:
            if hint.lower() in text:
                score += 4
        for trigger in spec.routing.default_when_user_mentions:
            if trigger.lower() in text:
                score += 10
        if score > best_score:
            best_score = score
            best_id = spec.id
    return best_id
