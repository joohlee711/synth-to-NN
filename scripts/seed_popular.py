"""Pre-seed the SQLite cache with popular modules' function tags.

Walks one or more 'popular modules' collection racks via the existing
polite fetcher (2s interval, deduplicated cache). After running, first-
time classifications for typical users get cache hits for most modules.

Usage:
    python -m scripts.seed_popular
    python -m scripts.seed_popular https://modulargrid.net/e/racks/view/816665 ...

Default seeds the '54 Most Popular Modules' rack (id 816665). Total time
on a cold cache: ~2 minutes (54 modules x 2s polite interval).
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import fetcher, parser  # noqa: E402

DEFAULT_RACKS = [
    "https://modulargrid.net/e/racks/view/816665",
]


def seed(rack_urls: list[str]) -> int:
    fetched_total = 0
    started = time.monotonic()
    for url in rack_urls:
        parsed_url = parser.parse_rack_url(url)
        if not parsed_url:
            print(f"skip: not a rack URL: {url}", flush=True)
            continue
        fmt, rack_id = parsed_url
        print(f"== rack {rack_id} ({url}) ==", flush=True)
        rack = fetcher.get_rack(rack_id, fmt=fmt)
        modules = rack["modules"]
        for i, mod in enumerate(modules, 1):
            m = fetcher.get_module(mod["id"], mod["slug"])
            n_tags = len(m.get("function_names", {}))
            print(
                f"  [{i:>3}/{len(modules)}] {mod['name']:32.32s}  {n_tags} tags",
                flush=True,
            )
            fetched_total += 1
    elapsed = time.monotonic() - started
    print(f"\nseeded {fetched_total} module fetches in {elapsed:.0f}s", flush=True)
    return fetched_total


if __name__ == "__main__":
    urls = sys.argv[1:] or DEFAULT_RACKS
    seed(urls)
