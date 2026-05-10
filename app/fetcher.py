import json
import os
import time
from typing import Callable

import httpx

from . import db, parser

UA = os.environ.get(
    "USER_AGENT",
    "synth-to-nn/0.1 (+https://github.com/joohlee711/synth-to-nn)",
)
_HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"}
_MIN_INTERVAL_S = 2.0
_last_request_at: float = 0.0

Fetcher = Callable[[str], str]


def polite_get(url: str) -> str:
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    if elapsed < _MIN_INTERVAL_S:
        time.sleep(_MIN_INTERVAL_S - elapsed)
    with httpx.Client(headers=_HEADERS, timeout=15.0, follow_redirects=True) as c:
        r = c.get(url)
        r.raise_for_status()
        _last_request_at = time.monotonic()
        return r.text


def get_rack(rack_id: str | int, fmt: str = "e", *, fetch: Fetcher = polite_get) -> dict:
    rid = int(rack_id)
    with db.connect() as conn:
        row = conn.execute(
            "SELECT raw_json FROM racks WHERE rack_id = ?", (rid,)
        ).fetchone()
        if row:
            return json.loads(row["raw_json"])

    html = fetch(f"https://modulargrid.net/{fmt}/racks/view/{rid}")
    parsed = parser.parse_rack_html(html)

    with db.connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO racks (rack_id, format, name, raw_json) VALUES (?,?,?,?)",
            (int(parsed["rack_id"]), parsed["format"], parsed["name"], json.dumps(parsed)),
        )
    return parsed


def get_module(module_id: int, slug: str, *, fetch: Fetcher = polite_get) -> dict:
    with db.connect() as conn:
        row = conn.execute(
            "SELECT module_id FROM modules WHERE module_id = ?", (module_id,)
        ).fetchone()
        if row:
            fns = conn.execute(
                """
                SELECT mf.function_id, ft.name
                FROM module_functions mf
                LEFT JOIN function_taxonomy ft USING (function_id)
                WHERE mf.module_id = ?
                """,
                (module_id,),
            ).fetchall()
            return {
                "id": module_id,
                "function_ids": [r["function_id"] for r in fns],
                "function_names": {
                    r["function_id"]: r["name"] for r in fns if r["name"]
                },
            }

    html = fetch(f"https://modulargrid.net/e/{slug}")
    parsed = parser.parse_module_html(html)

    with db.connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO modules (module_id, slug) VALUES (?,?)",
            (module_id, slug),
        )
        conn.executemany(
            "INSERT OR IGNORE INTO module_functions (module_id, function_id) VALUES (?,?)",
            [(module_id, fid) for fid in parsed["function_ids"]],
        )
        conn.executemany(
            "INSERT OR IGNORE INTO function_taxonomy (function_id, name) VALUES (?,?)",
            [(fid, name) for fid, name in parsed["function_names"].items()],
        )
    return parsed
