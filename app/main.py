from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import fetcher, matcher, parser

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="synth-to-nn")


class ClassifyRequest(BaseModel):
    rack_url: str


@app.post("/api/classify")
def classify(req: ClassifyRequest):
    parsed_url = parser.parse_rack_url(req.rack_url)
    if not parsed_url:
        raise HTTPException(400, "Not a ModularGrid rack URL")
    fmt, rack_id = parsed_url

    rack = fetcher.get_rack(rack_id, fmt=fmt)

    function_names: list[str] = []
    for mod in rack["modules"]:
        m = fetcher.get_module(mod["id"], mod["slug"])
        function_names.extend(m["function_names"].values())

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
        "matched_functions": result["matched_functions"],
        "unmatched_functions": result["unmatched_functions"],
    }


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
