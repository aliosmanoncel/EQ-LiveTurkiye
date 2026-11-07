"""Tests for the static site product data/reasenberg_gk74_emsc.json (WORKFLOW 1G).

Publication criterion (decision 2026-11-07): the committed file is reproducible from the
catalog and the frozen code, is strict JSON (browser JSON.parse), and — for the catalog
version analysed on 2026-11-02 — reproduces the analysis numbers exactly.
"""

import hashlib
import json
import math
import os
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import build_reasenberg_gk74_compare as B  # noqa: E402
import decluster_reasenberg as D  # noqa: E402

PRODUCT = ROOT / B.OUTPUT
ANALYSED_CATALOG_SHA256 = "bd303aa30a17ae590073cfe664fd58c87cf93ed643cdb8374aa33c27a6d7545b"


@pytest.fixture(scope="module")
def committed():
    return json.loads(PRODUCT.read_text(encoding="utf-8"), parse_constant=_reject)


@pytest.fixture(scope="module")
def rebuilt():
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        return json.loads(json.dumps(D.json_safe(B.build()), allow_nan=False, ensure_ascii=False))
    finally:
        os.chdir(cwd)


def _reject(name):
    raise ValueError(f"non-standard JSON constant {name}")


def test_strict_json(committed):
    # parse_constant raises on Infinity / NaN, as a browser would
    assert committed["methods"]["reasenberg"]["params"]["r_max"] == "inf"


def test_reproducible_from_catalog_and_code(committed, rebuilt):
    assert rebuilt == committed, ("data/reasenberg_gk74_emsc.json is stale: "
                                  "run python scripts/build_reasenberg_gk74_compare.py")


def test_same_events_and_definition(committed):
    d = committed["definition"]
    assert d["same_events_both_methods"] is True
    assert d["source"] == "EMSC" and d["mag_min"] == 3.0 and d["period"].startswith("1998")
    assert committed["methods"]["reasenberg"]["rule"] == "zmap"
    assert committed["methods"]["reasenberg"]["module_sha256"] == D.MODULE_SHA256_FROZEN


def test_internal_consistency(committed):
    t, k = committed["totals"], committed["categories"]
    n = t["n"]
    assert sum(k.values()) == n
    assert k["both_independent"] + k["GK_only_independent"] == t["gk74"]["independent"]
    assert k["both_independent"] + k["R_only_independent"] == t["reasenberg"]["independent"]
    rb = t["reasenberg"]
    assert rb["single"] + rb["representative"] + rb["dependent"] + rb["invalid"] == n
    assert rb["dependent_foreshock"] + rb["dependent_aftershock"] == rb["dependent"]
    assert rb["representative"] == rb["clusters"]
    for key in ("by_magnitude", "by_year", "by_boundary_distance"):
        assert sum(b["n"] for b in committed[key]) == n
    assert all(c["n"] >= committed["cells"]["min_n"] for c in committed["cells"]["items"])
    assert math.isclose(committed["agreement_rate"],
                        round((k["both_independent"] + k["both_dependent"]) / n, 4))


def test_matches_analysis_numbers_for_analysed_catalog(committed):
    if committed["definition"]["catalog_sha256"] != ANALYSED_CATALOG_SHA256:
        pytest.skip("catalog changed since the 2026-11-02 analysis; numbers are not comparable")
    t, k = committed["totals"], committed["categories"]
    assert (t["n"], t["gk74"]["independent"], t["reasenberg"]["independent"], t["reasenberg"]["clusters"]) \
        == (80929, 35300, 65942, 2080)
    assert k == {"both_independent": 34966, "both_dependent": 14653,
                 "R_only_independent": 30976, "GK_only_independent": 334}


def test_adapter_output_is_strict_json(tmp_path):
    cat = tmp_path / "c.json"
    cat.write_text(json.dumps(dict(events=[dict(id="a", time="2020-01-01T00:00:00Z", lat=38, lon=35, dep=10, mag=3),
                                           dict(id="b", time="2020-01-01T01:00:00Z", lat=38.001, lon=35, dep=10, mag=3)])))
    out = tmp_path / "o.json"
    D.main(["--xmeff", "3.0", "--input", str(cat), "--output", str(out)])
    txt = out.read_text(encoding="utf-8")
    assert "Infinity" not in txt and "NaN" not in txt
    json.loads(txt, parse_constant=_reject)
