import html as html_mod
import json
import re

_RTD_RE = re.compile(r'data-mg-json="rtd">(.*?)</script>', re.S)
_TAGS_BLOCK_RE = re.compile(r'<div class="module-tags">(.*?)</div>', re.S)
_TAG_RE = re.compile(
    r'SearchFunction=(\d+)[^>]*>\s*<span class="badge text-bg-func">([^<]+)</span>'
)
_MODULE_ID_RE = re.compile(r'data-module-id="(\d+)"')
_RACK_URL_RE = re.compile(r"modulargrid\.net/([a-z])/racks/view/(\d+)", re.I)


def parse_rack_url(url: str) -> tuple[str, str] | None:
    m = _RACK_URL_RE.search(url)
    return (m.group(1), m.group(2)) if m else None


def parse_rack_html(text: str) -> dict:
    m = _RTD_RE.search(text)
    if not m:
        raise ValueError("rtd JSON blob not found in rack HTML")
    rtd = json.loads(html_mod.unescape(m.group(1)))
    rack = rtd["rack"]["Rack"]
    return {
        "rack_id": rack["id"],
        "name": rack["name"],
        "format": rack["format"],
        "user": rtd["rack"]["User"]["username"],
        "modules": [
            {
                "id": int(mod["id"]),
                "name": mod["name"],
                "slug": mod["slug"],
                "vendor": mod["Vendor"]["name"],
                "hp": int(mod["te"]) if mod["te"] else None,
            }
            for mod in rtd["rack"]["Module"]
        ],
    }


def parse_module_html(text: str) -> dict:
    mid_m = _MODULE_ID_RE.search(text)
    if not mid_m:
        raise ValueError("module-id not found in module HTML")
    block_m = _TAGS_BLOCK_RE.search(text)
    tags = _TAG_RE.findall(block_m.group(1)) if block_m else []
    return {
        "id": int(mid_m.group(1)),
        "function_ids": [int(fid) for fid, _ in tags],
        "function_names": {int(fid): name for fid, name in tags},
    }
