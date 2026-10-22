# Author: JunyoungJung
# Date: 2026-10-22
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "verify"


@pytest.fixture(scope="session")
def root() -> pathlib.Path:
    return ROOT


@pytest.fixture(scope="session")
def skill() -> pathlib.Path:
    return SKILL
