from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any


def to_json(obj: Any) -> str:
    try:
        if hasattr(obj, "__dict__"):
            return json.dumps(obj.__dict__, indent=2)
        return json.dumps(obj, indent=2)
    except TypeError:
        try:
            return json.dumps(asdict(obj), indent=2)
        except Exception:
            return json.dumps(str(obj))
