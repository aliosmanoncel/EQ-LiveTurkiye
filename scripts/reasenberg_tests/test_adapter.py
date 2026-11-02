"""Tests for scripts/decluster_reasenberg.py (EQ-Live adapter) and the module freeze.

Run from the repository root:  python -m pytest -q scripts/reasenberg_tests
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import decluster_reasenberg as D  # noqa: E402
import reasenberg as R  # noqa: E402

FIXTURES = sorted((SCRIPTS / "fixtures").glob("reasenberg_zmap_*_ref.json"))


def ev(i, time, lat=38.0, lon=35.0, dep=10.0, mag=3.0, **kw):
    return dict(id=f"e{i}", time=time, lat=lat, lon=lon, dep=dep, mag=mag, **kw)


# ---------------------------------------------------------------- freeze
def test_module_is_frozen_v030():
    assert R.__version__ == "0.3.0"
    assert D.module_sha256() == D.MODULE_SHA256_FROZEN


def test_cli_refuses_modified_module(monkeypatch, tmp_path):
    monkeypatch.setattr(D, "module_sha256", lambda: "0" * 64)
    with pytest.raises(SystemExit):
        D.main(["--xmeff", "3.0", "--input", str(tmp_path / "x.json"), "--output", str(tmp_path / "y.json")])


# ---------------------------------------------------------------- adapter behaviour
def test_doublet_classes_and_default_rule():
    evs, out = D.decluster([ev(1, "2020-01-01T00:00:00Z"), ev(2, "2020-01-01T01:00:00Z", lat=38.001, mag=3.5)], 3.0)
    cls = dict(zip([e["id"] for e in evs], out["event_class"]))
    assert cls == {"e1": "dependent", "e2": "representative"}
    assert out["res"].params.rule == "zmap"


def test_invalid_events_kept_not_clustered():
    events = [ev(1, "2020-01-01T00:00:00Z"), ev(2, "2020-01-01T01:00:00Z", lat=38.001),
              ev(3, None), ev(4, "2020-01-01T02:00:00Z", dep=None), ev(5, "2020-01-01T03:00:00Z", mag="x")]
    evs, out = D.decluster(events, 3.0)
    cls = dict(zip([e["id"] for e in evs], out["event_class"]))
    assert cls["e3"] == cls["e4"] == cls["e5"] == "invalid"
    assert all(i for e, i in zip(evs, out["independent"]) if e["id"] in ("e3", "e4", "e5"))
    assert evs[-1]["id"] == "e3"                       # invalid time sorted last (as GK74)


def test_mag_field_mw_uses_mw_then_mag():
    e1 = ev(1, "2020-01-01T00:00:00Z", mag=3.0, mw=5.0)
    e2 = ev(2, "2020-01-01T01:00:00Z", lat=38.05, mag=4.0)      # 5.6 km away
    _, a = D.decluster([e1, e2], 3.0, mag_field="mag")
    _, b = D.decluster([e1, e2], 3.0, mag_field="mw")
    assert a["event_class"] == ["single", "single"]             # 10 r(4.0) = 4.4 km < 5.6 km
    assert b["event_class"] == ["representative", "dependent"]  # 10 r(5.0) = 11 km


def test_time_parsing_is_utc_and_tz_independent(tmp_path):
    cat = tmp_path / "c.json"
    events = [ev(1, "2020-03-29T00:30:00"), ev(2, "2020-03-29T01:20:00Z", lat=38.001),
              ev(3, "2020-03-29T05:00:00+03:00", lat=38.002)]
    cat.write_text(json.dumps(dict(events=events)))
    outs = []
    for tz in ("UTC", "Europe/Istanbul"):
        o = tmp_path / f"o_{tz.replace('/', '_')}.json"
        subprocess.run([sys.executable, str(SCRIPTS / "decluster_reasenberg.py"), "--xmeff", "3.0",
                        "--input", str(cat), "--output", str(o), "--membership"],
                       check=True, capture_output=True, env={**os.environ, "TZ": tz}, cwd=ROOT)
        outs.append(json.loads(o.read_text())["membership"])
    assert outs[0] == outs[1]


def test_cli_output_provenance(tmp_path):
    cat = tmp_path / "c.json"
    cat.write_text(json.dumps(dict(source="test", events=[ev(1, "2020-01-01T00:00:00Z"),
                                                          ev(2, "2020-01-01T01:00:00Z", lat=38.001)])))
    o = tmp_path / "o.json"
    r = D.main(["--xmeff", "3.0", "--input", str(cat), "--output", str(o), "--equivalent", "--rule", "cluster2000x"])
    rb = r["reasenberg"]
    assert rb["rule"] == "cluster2000x" and rb["rule_status"] == "experimental"
    assert rb["module_sha256"] == D.MODULE_SHA256_FROZEN and rb["module_version"] == "0.3.0"
    assert rb["input_sha256"] == hashlib.sha256(cat.read_bytes()).hexdigest()
    assert r["original_n"] == 2 and r["main_n"] == 1 and r["removed_n"] == 1
    assert len(r["equivalent_events_sensitivity_only"]) == 1
    assert json.loads(o.read_text())["count"] == 1


# ---------------------------------------------------------------- frozen regression references
def test_fixtures_present():
    assert len(FIXTURES) == 4


@pytest.mark.parametrize("fx_path", FIXTURES, ids=lambda p: p.stem)
def test_frozen_regression_reference(fx_path):
    fx = json.loads(fx_path.read_text(encoding="utf-8"))
    raw = (ROOT / fx["catalog"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == fx["catalog_sha256"], "fixture catalog changed"
    assert fx["module_sha256"] == D.MODULE_SHA256_FROZEN
    P = fx["params"]
    evs, out = D.decluster(json.loads(raw.decode("utf-8"))["events"], P["xmeff"], P["rule"], P["mag_field"])
    assert [[e["id"], c, k] for e, c, k in zip(evs, out["cluster_id"], out["event_class"])] == fx["membership"]
    assert sorted(e["id"] for e, i in zip(evs, out["independent"]) if i) == fx["independent_ids"]
