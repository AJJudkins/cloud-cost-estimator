"""Estimate monthly cost from a resource list using a bundled EXAMPLE price table.
Prices are illustrative only and are NOT real quotes."""
import argparse
import json
from pathlib import Path

DEFAULT_PRICES = Path(__file__).parent / "data" / "prices.json"
DISCLAIMER = "NOTE: uses example prices only. This is not a real quote."


def load_file(path):
    text = Path(path).read_text()
    if str(path).lower().endswith((".yaml", ".yml")):
        import yaml  # PyYAML, only needed for YAML input
        return yaml.safe_load(text)
    return json.loads(text)


def load_prices(path=DEFAULT_PRICES):
    return json.loads(Path(path).read_text())


def cost_item(item, prices):
    """Return (description, monthly cost) for one resource."""
    if not isinstance(item, dict):
        raise ValueError(f"resource must be a mapping, got {item!r}")
    t = item.get("type")
    for k in ("count", "gb", "hours_per_month"):
        if k in item and (isinstance(item[k], bool) or not isinstance(item[k], (int, float)) or item[k] < 0):
            raise ValueError(f"invalid resource {item}: '{k}' must be a non-negative number")
    hrs = item.get("hours_per_month", prices["hours_per_month"])
    n = item.get("count", 1)
    try:
        if t == "compute":
            return f"compute {item['size']} x{n}", prices["compute_per_hour"][item["size"]] * hrs * n
        if t == "database":
            return f"database {item['size']} x{n}", prices["database_per_hour"][item["size"]] * hrs * n
        if t == "storage":
            return f"storage {item['tier']} {item['gb']}GB", prices["storage_gb_month"][item["tier"]] * item["gb"]
        if t == "load_balancer":
            return f"load balancer x{n}", prices["load_balancer_month"] * n
        if t == "data_transfer":
            return f"data transfer {item['gb']}GB", prices["data_transfer_gb"] * item["gb"]
    except KeyError as e:
        raise ValueError(f"invalid resource {item}: unknown or missing {e}") from None
    raise ValueError(f"unknown resource type: {t!r}")


def estimate(resources, prices):
    lines = [cost_item(r, prices) for r in resources]
    return {"items": [{"item": d, "monthly_usd": round(c, 2)} for d, c in lines],
            "total_monthly_usd": round(sum(c for _, c in lines), 2)}


def format_report(result):
    out = [f"{'Resource':<32}{'USD/month':>10}"]
    out += [f"{i['item']:<32}{i['monthly_usd']:>10.2f}" for i in result["items"]]
    out += ["-" * 42, f"{'TOTAL':<32}{result['total_monthly_usd']:>10.2f}", DISCLAIMER]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Monthly cloud cost estimator (example prices)")
    ap.add_argument("resources", help="YAML or JSON file with a top-level 'resources' list")
    ap.add_argument("--prices", default=str(DEFAULT_PRICES))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        data = load_file(a.resources)
        if not isinstance(data, dict) or not isinstance(data.get("resources"), list):
            raise ValueError("input must contain a top-level 'resources' list")
        result = estimate(data["resources"], load_prices(a.prices))
    except (OSError, ValueError, KeyError, ImportError) as e:
        ap.exit(1, f"error: {e}\n")
    result["disclaimer"] = DISCLAIMER
    print(json.dumps(result, indent=2) if a.json else format_report(result))


if __name__ == "__main__":
    main()
