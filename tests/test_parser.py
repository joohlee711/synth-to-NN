from app import parser


def test_parse_rack_url_valid():
    assert parser.parse_rack_url(
        "https://modulargrid.net/e/racks/view/816665"
    ) == ("e", "816665")


def test_parse_rack_url_other_format():
    assert parser.parse_rack_url(
        "https://modulargrid.net/a/racks/view/12345"
    ) == ("a", "12345")


def test_parse_rack_url_invalid():
    assert parser.parse_rack_url("https://example.com/foo") is None


def test_parse_rack(rack_html):
    rack = parser.parse_rack_html(rack_html)
    assert rack["rack_id"] == "816665"
    assert rack["name"] == "54 Most Popular Modules"
    assert rack["format"] == "e"
    assert rack["user"] == "Palsen"
    assert len(rack["modules"]) == 54

    maths = next(m for m in rack["modules"] if m["name"] == "Maths")
    assert maths["id"] == 2697
    assert maths["vendor"] == "Make Noise"
    assert maths["hp"] == 20
    assert maths["slug"] == "make-noise-maths--"


def test_parse_module(module_html):
    mod = parser.parse_module_html(module_html)
    assert mod["id"] == 2697
    assert sorted(mod["function_ids"]) == [3, 4, 15, 28, 29, 30, 37, 39]
    assert mod["function_names"][3] == "LFO"
    assert mod["function_names"][37] == "Logic"
    assert mod["function_names"][39] == "Function Generator"
