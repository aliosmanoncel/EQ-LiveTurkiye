"""Regression tests for the decisions approved on 2026-11-02.

D2: output for GK74 comparison = representative (largest event);
    equivalent events only as a separate sensitivity product.
D3: default rule stays 'zmap'; 'cluster2000x' is experimental until the
    event-level Fortran validation (D1) is done; the rule is always recorded.
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reasenberg import (  # noqa: E402
    CLUSTER2000X_DEFAULTS, REPRESENTATIVE, ExperimentalRuleWarning, reasenberg,
)

T, X, M = [0.0, 0.1], [0.0, 0.5], [3.0, 4.0]


def run(**kw):
    return reasenberg(T, X, [0, 0], [10, 10], M, xmeff=2.0, coords="cartesian", **kw)


def test_default_rule_is_zmap_and_silent():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        r = run()
    assert r.params.rule == "zmap"
    assert r.summary()["rule_status"] == "default"


def test_cluster2000x_emits_experimental_warning():
    with pytest.warns(ExperimentalRuleWarning):
        r = run(**CLUSTER2000X_DEFAULTS)
    assert r.summary()["rule_status"] == "experimental"


def test_experimental_warning_is_not_a_userwarning():
    # must not be confused with data-quality warnings (e.g. M < xmeff)
    assert not issubclass(ExperimentalRuleWarning, UserWarning)


def test_summary_records_provenance():
    s = run().summary()
    for key in ("module_version", "rule", "rule_status", "output", "params"):
        assert key in s
    assert s["output"].startswith("representative")


@pytest.mark.parametrize("rule", ["zmap", "cluster2000x"])
def test_default_output_is_largest_event(rule):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ExperimentalRuleWarning)
        r = run(rule=rule)
    assert r.representative.tolist() == [1]
    assert r.event_class[1] == REPRESENTATIVE
    assert np.asarray(M)[r.independent].max() == 4.0
