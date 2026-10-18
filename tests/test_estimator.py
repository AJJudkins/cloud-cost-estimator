import json, os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import estimator as e

P = e.load_prices()


def test_compute_cost():
    _, c = e.cost_item({"type": "compute", "size": "medium", "count": 2}, P)
    assert c == pytest.approx(0.05 * 730 * 2)


def test_custom_hours_and_storage():
    assert e.cost_item({"type": "compute", "size": "small", "hours_per_month": 100}, P)[1] == pytest.approx(2.0)
    assert e.cost_item({"type": "storage", "tier": "standard", "gb": 100}, P)[1] == pytest.approx(2.0)


def test_total():
    r = e.estimate([{"type": "load_balancer"}, {"type": "data_transfer", "gb": 100}], P)
    assert r["total_monthly_usd"] == 26.0


def test_unknown_type_and_size():
    with pytest.raises(ValueError):
        e.cost_item({"type": "teleporter"}, P)
    with pytest.raises(ValueError):
        e.cost_item({"type": "compute", "size": "gigantic"}, P)


def test_yaml_and_json_inputs(tmp_path):
    y = e.load_file(os.path.join(os.path.dirname(__file__), "..", "resources.example.yaml"))
    assert e.estimate(y["resources"], P)["total_monthly_usd"] > 0
    j = tmp_path / "r.json"
    j.write_text(json.dumps({"resources": [{"type": "load_balancer"}]}))
    assert e.estimate(e.load_file(str(j))["resources"], P)["total_monthly_usd"] == 18.0


def test_report_has_disclaimer():
    assert "not a real quote" in e.format_report(e.estimate([], P))


import json as _json
import pytest as _pytest


def test_negative_and_bad_values_rejected():
    import estimator
    prices = estimator.load_prices()
    for item in ({"type": "storage", "tier": "standard", "gb": -5},
                 {"type": "compute", "size": "small", "count": "two"},
                 "not-a-dict"):
        with _pytest.raises(ValueError):
            estimator.cost_item(item, prices)


def test_cli_reports_clean_errors(tmp_path):
    import estimator
    bad = tmp_path / "r.json"
    bad.write_text(_json.dumps({"nope": []}))
    with _pytest.raises(SystemExit) as e:
        estimator.main([str(bad)])
    assert e.value.code == 1
    with _pytest.raises(SystemExit) as e:
        estimator.main([str(tmp_path / "missing.json")])
    assert e.value.code == 1
