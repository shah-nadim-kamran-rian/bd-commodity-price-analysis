"""
Step 2 of the pipeline.

Runs every query in sql/analysis.sql against the clean data using DuckDB,
saves each result to outputs/ as a CSV and collects them in outputs/sql_results.md.

Run from the project root:
    python src/02_run_queries.py
"""

from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN_FILE = ROOT / "data" / "processed" / "commodity_prices_clean.csv"
SQL_FILE = ROOT / "sql" / "analysis.sql"
OUT_DIR = ROOT / "outputs"


def load_queries(path: Path) -> list[tuple[str, str]]:
    """Split the SQL file into (name, query) pairs using the '-- name:' tags."""
    text = path.read_text(encoding="utf-8")
    queries = []
    for block in text.split("-- name:")[1:]:
        name, _, body = block.partition("\n")
        queries.append((name.strip(), body.strip().rstrip(";")))
    return queries


def describe(query: str) -> str:
    """Turn the comment lines under a name tag into a one-line description."""
    notes = [line.lstrip("- ").strip() for line in query.splitlines() if line.startswith("--")]
    return " ".join(notes)


def main() -> None:
    if not CLEAN_FILE.exists():
        raise SystemExit("Clean file not found. Run src/01_clean_data.py first.")

    con = duckdb.connect()
    con.register("market_prices", pd.read_csv(CLEAN_FILE))

    OUT_DIR.mkdir(exist_ok=True)
    report = [
        "# SQL results",
        "",
        "Output of the queries in sql/analysis.sql. Regenerate with python src/02_run_queries.py.",
        "",
    ]

    for name, query in load_queries(SQL_FILE):
        result = con.execute(query).df()
        result.to_csv(OUT_DIR / f"{name}.csv", index=False)
        report += [f"## {name}", "", describe(query), "", result.to_markdown(index=False), ""]
        print(f"{name}: {len(result)} rows")

    (OUT_DIR / "sql_results.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Saved results to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
