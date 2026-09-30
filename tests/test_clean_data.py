"""
Unit tests for the cleaning step. Run from the project root:
    python -m pytest
"""

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

# The script name starts with a number, so it is loaded from its path.
SCRIPT = Path(__file__).resolve().parents[1] / "src" / "01_clean_data.py"
spec = importlib.util.spec_from_file_location("clean_data", SCRIPT)
clean_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clean_data)


def raw_rows(prices=(60.0,), **overrides):
    """Build a small raw DataFrame shaped like the real file."""
    base = {
        "Session": " summer ",
        "Market": "Karwan  Bazar (Dhaka)",
        "Commodity": "rice",
        "Variety": "BR-28 Rice",
        "Unit": "Kg",
        "Purchase_Price": 60.0,
        "Stock_Level": "LOW",
        "Weather": "sunny",
        "Seasonal_Harvest": "yes",
        "Festival_or_Event": "No",
        "Day_of_Week": "monday",
    }
    base.update(overrides)
    return pd.DataFrame([{**base, "Purchase_Price": p} for p in prices])


def test_label_columns_are_trimmed_and_title_cased():
    out = clean_data.clean(raw_rows())
    assert out.loc[0, "season"] == "Summer"
    assert out.loc[0, "market"] == "Karwan Bazar (Dhaka)"
    assert out.loc[0, "stock_level"] == "Low"
    assert out.loc[0, "seasonal_harvest"] == "Yes"


def test_variety_keeps_its_original_case():
    out = clean_data.clean(raw_rows())
    assert out.loc[0, "variety"] == "BR-28 Rice"


def test_city_and_stock_order_are_added():
    out = clean_data.clean(raw_rows())
    assert out.loc[0, "city"] == "Dhaka"
    assert out.loc[0, "stock_order"] == 1


def test_rows_without_a_price_are_dropped():
    out = clean_data.clean(raw_rows(prices=(60.0, None)))
    assert len(out) == 1


def test_columns_outside_the_rename_map_are_dropped():
    raw = raw_rows()
    raw["Unused_Column"] = 1
    out = clean_data.clean(raw)
    assert list(out.columns) == clean_data.BASE_COLS


def test_validate_rejects_unknown_stock_level():
    out = clean_data.clean(raw_rows(Stock_Level="Very Low"))
    with pytest.raises(ValueError):
        clean_data.validate(out)


def test_price_anomaly_flags_only_prices_well_above_the_peer_median():
    # Median is 100, so only the 130 row is more than 15% above it.
    out = clean_data.add_price_anomaly(clean_data.clean(raw_rows(prices=(100, 100, 100, 110, 130))))
    assert out["price_anomaly"].tolist() == [0, 0, 0, 0, 1]
    assert out.loc[4, "pct_vs_peer"] == 30.0


def test_price_exactly_on_the_threshold_is_not_an_anomaly():
    out = clean_data.add_price_anomaly(clean_data.clean(raw_rows(prices=(100, 100, 115))))
    assert out["price_anomaly"].tolist() == [0, 0, 0]
