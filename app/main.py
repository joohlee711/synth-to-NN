import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import archetypes, fetcher, matcher, parser

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="synth-to-nn")


class ClassifyRequest(BaseModel):
    rack_url: str


def _resolve_rack(rack_url: str) -> tuple[str, str]:
    parsed_url = parser.parse_rack_url(rack_url)
    if not parsed_url:
        raise HTTPException(400, "Not a ModularGrid rack URL")
    return parsed_url


def _build_payload(rack: dict, function_names: list[str]) -> dict:
    result = matcher.score_rack(function_names)
    return {
        "rack": {
            "id": rack["rack_id"],
            "name": rack["name"],
            "user": rack.get("user"),
        },
        "module_count": len(rack["modules"]),
        "function_count": len(function_names),
        "scores": result["scores"],
        "function_counts": result["function_counts"],
        "matched_functions": result["matched_functions"],
        "unmatched_functions": result["unmatched_functions"],
    }


@app.post("/api/classify")
def classify(req: ClassifyRequest):
    fmt, rack_id = _resolve_rack(req.rack_url)
    archetypes.reload()
    rack = fetcher.get_rack(rack_id, fmt=fmt)
    function_names: list[str] = []
    for mod in rack["modules"]:
        m = fetcher.get_module(mod["id"], mod["slug"])
        function_names.extend(m["function_names"].values())
    return _build_payload(rack, function_names)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.get("/api/classify-stream")
def classify_stream(rack_url: str):
    fmt, rack_id = _resolve_rack(rack_url)

    def gen():
        try:
            archetypes.reload()
            rack = fetcher.get_rack(rack_id, fmt=fmt)
        except Exception as e:
            yield _sse("fail", {"detail": f"rack fetch failed: {e}"})
            return

        modules = rack["modules"]
        yield _sse("meta", {
            "rack": {
                "id": rack["rack_id"],
                "name": rack["name"],
                "user": rack.get("user"),
            },
            "total_modules": len(modules),
        })

        function_names: list[str] = []
        for i, mod in enumerate(modules, 1):
            try:
                m = fetcher.get_module(mod["id"], mod["slug"])
                function_names.extend(m["function_names"].values())
            except Exception as e:
                yield _sse("warn", {"i": i, "name": mod["name"], "error": str(e)})
                continue
            yield _sse("progress", {
                "i": i,
                "total": len(modules),
                "name": mod["name"],
            })

        yield _sse("done", _build_payload(rack, function_names))

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz")
def healthz():
    return {"ok": True}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
