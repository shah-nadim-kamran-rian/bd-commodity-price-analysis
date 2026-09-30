"""
Step 1 of the pipeline.

Loads the raw commodity price file, reports missing values and duplicates,
tidies the text columns, derives a price anomaly flag and writes a clean
copy for SQL and Excel.

Run from the project root:
    python src/01_clean_data.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "bd_commodity_market.csv"
CLEAN_FILE = ROOT / "data" / "processed" / "commodity_prices_clean.csv"

# snake_case names are easier to work with in SQL.
# "Session" actually holds the season (Summer, Monsoon, Winter), so it gets a clearer name.
# Raw columns not listed here are dropped.
RENAME = {
    "Session": "season",
    "Market": "market",
    "Commodity": "commodity",
    "Variety": "variety",
    "Unit": "unit",
    "Purchase_Price": "purchase_price",
    "Stock_Level": "stock_level",
    "Weather": "weather",
    "Seasonal_Harvest": "seasonal_harvest",
    "Festival_or_Event": "festival_or_event",
    "Day_of_Week": "day_of_week",
}

# Columns with a small, fixed set of labels. Title case merges "low", "LOW" and "Low".
LABEL_COLS = [
    "season", "market", "commodity", "stock_level", "weather",
    "seasonal_harvest", "festival_or_event", "day_of_week",
]

# Kept in their original case on purpose: title case would turn "BR-28 Rice" into "Br-28 Rice".
KEEP_CASE_COLS = ["variety", "unit"]

STOCK_ORDER = {"Low": 1, "Medium": 2, "High": 3}
MARKET_CITY = {"Karwan Bazar (Dhaka)": "Dhaka"}

# A purchase is an anomaly when it costs more than this much above the median
# price paid for the same variety in the same season. 15% is a business rule,
# not a statistical law, so change it here to test other cut-offs.
ANOMALY_THRESHOLD = 0.15
PEER_GROUP = ["commodity", "variety", "season"]

BASE_COLS = [
    "season", "market", "city", "commodity", "variety", "unit",
    "purchase_price", "stock_level", "stock_order", "weather",
    "seasonal_harvest", "festival_or_event", "day_of_week",
]


def load_raw(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    print(f"Loaded {len(df):,} rows and {df.shape[1]} columns from {path.name}")
    return df


def quality_report(df: pd.DataFrame) -> None:
    print()
    print("Missing values per column")
    print(df.isna().sum().to_string())

    # Duplicates are reported, not dropped. With no date column, two identical
    # rows can still be two genuine purchases made on different days.
    print()
    print(f"Exact duplicate rows: {df.duplicated().sum():,}")

    print()
    print("Purchase price by commodity (raw)")
    summary = df.groupby("Commodity")["Purchase_Price"].describe().round(2)
    print(summary.to_string())


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=RENAME)

    for col in LABEL_COLS + KEEP_CASE_COLS:
        # strip the edges and collapse repeated spaces inside the value
        df[col] = df[col].astype("string").str.split().str.join(" ")
    for col in LABEL_COLS:
        df[col] = df[col].str.title()

    df["purchase_price"] = pd.to_numeric(df["purchase_price"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["commodity", "market", "purchase_price"])
    if len(df) < before:
        print(f"Dropped {before - len(df):,} rows missing commodity, market or price")

    df["city"] = df["market"].replace(MARKET_CITY)
    df["stock_order"] = df["stock_level"].map(STOCK_ORDER).astype("Int64")
    return df[BASE_COLS].reset_index(drop=True)


def add_price_anomaly(df: pd.DataFrame) -> pd.DataFrame:
    """Compare each price with the median paid for the same variety in the same season."""
    df = df.copy()
    peer_median = df.groupby(PEER_GROUP)["purchase_price"].transform("median")
    df["peer_median_price"] = peer_median.round(2)
    df["pct_vs_peer"] = ((df["purchase_price"] / peer_median - 1) * 100).round(1)
# Compare the rounded percentage, not raw floats: 100 * 1.15 is 114.99999999999999
# in floating point, which would wrongly flag a price of exactly 115.
    df["price_anomaly"] = (df["pct_vs_peer"] > round(ANOMALY_THRESHOLD * 100, 1)).astype(int)
    return df


def validate(df: pd.DataFrame) -> None:
    problems = []

    if (df["purchase_price"] <= 0).any():
        problems.append("found zero or negative prices")

    unknown_stock = set(df["stock_level"].dropna()) - set(STOCK_ORDER)
    if unknown_stock:
        problems.append(f"unexpected stock levels: {sorted(unknown_stock)}")

    for col in ["seasonal_harvest", "festival_or_event"]:
        odd = set(df[col].dropna()) - {"Yes", "No"}
        if odd:
            problems.append(f"unexpected values in {col}: {sorted(odd)}")

    units = df.groupby("commodity")["unit"].nunique()
    if (units > 1).any():
        problems.append(f"mixed units for: {list(units[units > 1].index)}")

    if problems:
        raise ValueError("Data checks failed: " + "; ".join(problems))
    print()
    print("All data checks passed")


def main() -> None:
    df = load_raw(RAW_FILE)
    quality_report(df)
    df = clean(df)
    df = add_price_anomaly(df)
    validate(df)

    flagged = int(df["price_anomaly"].sum())
    print(f"Price anomalies: {flagged:,} rows ({flagged / len(df):.1%}) "
          f"more than {ANOMALY_THRESHOLD:.0%} above their peer median")

    CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False)
    print()
    print(f"Saved {len(df):,} clean rows to {CLEAN_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
