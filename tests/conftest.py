from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def rack_html() -> str:
    return (FIXTURES / "rack_816665.html").read_text()


@pytest.fixture
def module_html() -> str:
    return (FIXTURES / "module_2697_maths.html").read_text()
