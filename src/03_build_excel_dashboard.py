"""
Step 3 of the pipeline.

Builds an Excel dashboard from the clean data and the SQL outputs:
a summary page with KPI tiles, charts and heatmaps, an interactive
commodity explorer driven by Excel formulas, one sheet per SQL query,
the clean dataset as an Excel table and a notes page.

Run from the project root after steps 1 and 2:
    python src/03_build_excel_dashboard.py
"""

from pathlib import Path

import pandas as pd
import xlsxwriter
from xlsxwriter.utility import xl_range_abs, xl_rowcol_to_cell

ROOT = Path(__file__).resolve().parents[1]
CLEAN_FILE = ROOT / "data" / "processed" / "commodity_prices_clean.csv"
OUT_DIR = ROOT / "outputs"
DASHBOARD_FILE = ROOT / "dashboard" / "commodity_price_dashboard.xlsx"

# SQL result file -> sheet name. Excel caps sheet names at 31 characters.
QUERY_SHEETS = {
    "q1_price_by_commodity": "q1_commodity",
    "q2_price_by_commodity_market": "q2_market",
    "q3_price_by_stock_level": "q3_stock_level",
    "q4_low_vs_high_stock_premium": "q4_stock_premium",
    "q5_stock_premium_by_market": "q5_market_premium",
    "q6_anomaly_share_by_stock_level": "q6_anomaly_share",
    "q7_price_index_stock_anomaly": "q7_index_anomaly",
    "q8_weather_and_harvest": "q8_weather_harvest",
}

STOCK_LEVELS = ["Low", "Medium", "High"]
STOCK_COLORS = {"Low": "#C0392B", "Medium": "#95A5A6", "High": "#2E86AB"}
NAVY = "#1F3B57"
HEAT = {"type": "3_color_scale", "min_color": "#63BE7B", "mid_color": "#FFEB84", "max_color": "#F8696B"}

NOTES = [
    ("h", "What is in this workbook"),
    ("p", "Dashboard: KPI tiles, charts and market heatmaps built from the SQL results."),
    ("p", "Explorer: pick a commodity in the yellow cell to see prices by market and stock level. Everything on that sheet is an Excel formula."),
    ("p", "q1 to q8: the output of each query in sql/analysis.sql, unchanged."),
    ("p", "Data: the clean dataset as an Excel table, ready for filters and pivot tables."),
    ("h", "Definitions"),
    ("p", "CV % (coefficient of variation) = standard deviation / average x 100. It measures how spread out prices are, "
          "and works across items priced per kg and per litre."),
    ("p", "Price index = price / that commodity's average price x 100. 100 means an average price for that item."),
    ("p", "Price anomaly = a purchase more than 15% above the median price paid for the same variety in the same season."),
    ("p", "Low vs high gap = average price when stock is low compared with the average when stock is high."),
    ("h", "Limitations"),
    ("p", "There are no dates, so volatility means spread across purchases, not movement over time."),
    ("p", "The 15% anomaly cut-off is a business rule. It can be changed in src/01_clean_data.py."),
    ("p", "Stock level, weather and season can overlap, so these results show association, not cause."),
    ("p", "Some market and stock level combinations have only a few rows. Check n_low and n_high on q5_market_premium."),
]


def make_formats(wb):
    return {
        "title": wb.add_format({"bold": True, "font_size": 18, "font_color": NAVY}),
        "subtitle": wb.add_format({"italic": True, "font_color": "#666666"}),
        "tile_label": wb.add_format({"bold": True, "font_size": 9, "font_color": "white", "bg_color": NAVY,
                                     "align": "center", "valign": "vcenter"}),
        "tile_num": wb.add_format({"bold": True, "font_size": 16, "bg_color": "#EAF1F8", "num_format": "#,##0",
                                   "align": "center", "valign": "vcenter"}),
        "tile_text": wb.add_format({"bold": True, "font_size": 12, "bg_color": "#EAF1F8",
                                    "align": "center", "valign": "vcenter"}),
        "header": wb.add_format({"bold": True, "font_color": "white", "bg_color": NAVY, "border": 1, "align": "center"}),
        "section": wb.add_format({"bold": True, "font_size": 12, "font_color": NAVY}),
        "label": wb.add_format({"bold": True}),
        "input": wb.add_format({"bold": True, "bg_color": "#FFF2CC", "border": 2, "border_color": "#BF9000"}),
        "cell": wb.add_format({"border": 1}),
        "total": wb.add_format({"bold": True, "border": 1, "bg_color": "#EAF1F8"}),
        "price": wb.add_format({"num_format": "#,##0.00", "border": 1}),
        "int": wb.add_format({"num_format": "#,##0", "border": 1}),
        "pct": wb.add_format({"num_format": '0.0"%"', "border": 1}),
        "pct_signed": wb.add_format({"num_format": '+0.0"%";-0.0"%"', "border": 1}),
        "index": wb.add_format({"num_format": "0.0"}),
        "heat": wb.add_format({"num_format": '0.0"%"', "border": 1, "align": "center"}),
        "heat_signed": wb.add_format({"num_format": '+0.0"%";-0.0"%"', "border": 1, "align": "center"}),
        "caption": wb.add_format({"italic": True, "font_color": "#666666"}),
        "note": wb.add_format({"text_wrap": True, "valign": "top"}),
        "link": wb.add_format({"font_color": "#2E86AB", "underline": 1, "bold": True}),
        "tbl_price": wb.add_format({"num_format": "#,##0.00"}),
        "tbl_pct": wb.add_format({"num_format": '0.0"%"'}),
    }


def number_formats(f, df):
    """Pick a number format for each column based on its name."""
    formats = {}
    for col in df.columns:
        if col.endswith("_pct") or col == "pct_vs_peer":
            formats[col] = f["tbl_pct"]
        elif col.endswith("_index"):
            formats[col] = f["index"]
        elif col.startswith(("avg_", "min_", "max_")) or col in (
            "std_dev", "low_minus_high", "purchase_price", "peer_median_price"
        ):
            formats[col] = f["tbl_price"]
    return formats


def rows_of(df):
    """DataFrame rows as plain Python values, with NaN turned into empty cells."""
    return df.astype(object).where(df.notna(), None).values.tolist()


def write_table(ws, df, name, formats):
    """Write a DataFrame from A1 as a formatted Excel table and size the columns."""
    columns = []
    for col in df.columns:
        spec = {"header": col}
        if col in formats:
            spec["format"] = formats[col]
        columns.append(spec)
    ws.add_table(0, 0, len(df), len(df.columns) - 1, {
        "data": rows_of(df),
        "columns": columns,
        "name": name,
        "style": "Table Style Medium 2",
    })
    for i, col in enumerate(df.columns):
        width = max([len(col)] + [len(str(v)) for v in df[col].tolist()]) + 3
        ws.set_column(i, i, min(width, 28))


def col_ref(sheet, df, col):
    """Absolute reference to one column of a table that starts in A1, e.g. Data!$D$2:$D$1501."""
    idx = df.columns.get_loc(col)
    return f"{sheet}!" + xl_range_abs(1, idx, len(df), idx)


def chart_ref(sheet, df, col):
    """The same column as [sheet, first_row, col, last_row, col] for chart series."""
    idx = df.columns.get_loc(col)
    return [sheet, 1, idx, len(df), idx]


def write_q7_chart_data(ws, f, q7):
    """Pivot q7 next to its table (columns H to J) so the chart has one series per anomaly flag."""
    pivot = q7.pivot_table(index="stock_level", columns="price_anomaly", values="avg_price_index")
    pivot = pivot.reindex(index=[s for s in STOCK_LEVELS if s in pivot.index], columns=[0, 1])
    ws.write_row(0, 7, ["stock_level", "No anomaly flag", "Anomaly flagged"], f["header"])
    for i, (level, row) in enumerate(pivot.iterrows(), start=1):
        ws.write_string(i, 7, level)
        for j, value in enumerate(row, start=8):
            if pd.notna(value):
                ws.write_number(i, j, float(value), f["index"])
    ws.set_column(7, 9, 18)
    return len(pivot)


def write_heatmap(ws, f, table, first_row, first_col, title, cell_format):
    """Write a market x commodity grid and colour it green (low) to red (high)."""
    ws.write(first_row, first_col, title, f["section"])
    ws.write(first_row + 1, first_col, "Market", f["header"])
    for j, commodity in enumerate(table.columns):
        ws.write(first_row + 1, first_col + 1 + j, commodity, f["header"])
    for i, (market, row) in enumerate(table.iterrows()):
        r = first_row + 2 + i
        ws.write(r, first_col, market, f["cell"])
        for j, value in enumerate(row):
            if pd.notna(value):
                ws.write_number(r, first_col + 1 + j, float(value), cell_format)
            else:
                ws.write_blank(r, first_col + 1 + j, None, cell_format)
    last_row = first_row + 1 + len(table)
    ws.conditional_format(first_row + 2, first_col + 1, last_row, first_col + len(table.columns), HEAT)
    return last_row


def build_dashboard(wb, ws, f, data, results, q7_rows):
    q1 = results["q1_price_by_commodity"]
    q2 = results["q2_price_by_commodity_market"]
    q4 = results["q4_low_vs_high_stock_premium"]
    q5 = results["q5_stock_premium_by_market"]
    s1 = QUERY_SHEETS["q1_price_by_commodity"]
    s4 = QUERY_SHEETS["q4_low_vs_high_stock_premium"]
    s7 = QUERY_SHEETS["q7_price_index_stock_anomaly"]

    ws.hide_gridlines(2)
    ws.set_column("A:A", 2)
    ws.set_column("B:H", 13)
    ws.set_column("I:I", 22)
    ws.set_column("J:O", 13)
    ws.set_row(0, 28)
    ws.merge_range("B1:O1", "Bangladesh Commodity Prices: Stock Level and Price Volatility", f["title"])
    ws.merge_range("B2:O2", "Volatility here means spread across purchases (CV %), not change over time. "
                            "Source tables are on the q1 to q8 sheets.", f["subtitle"])

    # KPI tiles. The last two read the SQL result sheets, so they follow the data.
    commodity = col_ref("Data", data, "commodity")
    anomaly = col_ref("Data", data, "price_anomaly")
    cv, cv_names = col_ref(s1, q1, "cv_pct"), col_ref(s1, q1, "commodity")
    gap, gap_names = col_ref(s4, q4, "low_vs_high_pct"), col_ref(s4, q4, "commodity")
    tiles = [
        ("B", "C", "Records", f"=COUNTA({commodity})", f["tile_num"]),
        ("D", "E", "Commodities", f"=SUMPRODUCT(1/COUNTIF({commodity},{commodity}))", f["tile_num"]),
        ("F", "G", "Price anomalies",
         f'=TEXT(SUM({anomaly}),"#,##0")&" ("&TEXT(SUM({anomaly})/COUNT({anomaly}),"0%")&")"', f["tile_text"]),
        ("I", "K", "Least predictable price",
         f'=INDEX({cv_names},MATCH(MAX({cv}),{cv},0))&" ("&TEXT(MAX({cv}),"0.0")&"% CV)"', f["tile_text"]),
        ("L", "O", "Biggest low-stock markup",
         f'=INDEX({gap_names},MATCH(MAX({gap}),{gap},0))&" ("&TEXT(MAX({gap}),"+0.0;-0.0")&"%)"', f["tile_text"]),
    ]
    for first, last, label, formula, cell_format in tiles:
        ws.merge_range(f"{first}4:{last}4", label, f["tile_label"])
        ws.merge_range(f"{first}5:{last}5", "", cell_format)
        ws.write_formula(f"{first}5", formula, cell_format)
    ws.set_row(4, 32)

    spread = wb.add_chart({"type": "column"})
    spread.add_series({
        "name": "CV %",
        "categories": chart_ref(s1, q1, "commodity"),
        "values": chart_ref(s1, q1, "cv_pct"),
        "fill": {"color": NAVY},
        "data_labels": {"value": True, "num_format": '0.0"%"'},
    })
    spread.set_title({"name": "Price spread by commodity (CV %)"})
    spread.set_legend({"none": True})
    spread.set_y_axis({"num_format": '0"%"'})
    ws.insert_chart("B7", spread, {"x_scale": 1.25})

    premium = wb.add_chart({"type": "column"})
    premium.add_series({
        "name": "Low vs high stock",
        "categories": chart_ref(s4, q4, "commodity"),
        "values": chart_ref(s4, q4, "low_vs_high_pct"),
        "fill": {"color": STOCK_COLORS["Low"]},
        "data_labels": {"value": True, "num_format": '+0.0"%";-0.0"%"'},
    })
    premium.set_title({"name": "Low stock vs high stock price gap (%)"})
    premium.set_legend({"none": True})
    premium.set_y_axis({"num_format": '0"%"'})
    ws.insert_chart("I7", premium, {"x_scale": 1.25})

    index_chart = wb.add_chart({"type": "column"})
    for offset, (name, color) in enumerate([("No anomaly flag", STOCK_COLORS["High"]),
                                            ("Anomaly flagged", STOCK_COLORS["Low"])]):
        index_chart.add_series({
            "name": name,
            "categories": [s7, 1, 7, q7_rows, 7],
            "values": [s7, 1, 8 + offset, q7_rows, 8 + offset],
            "fill": {"color": color},
            "data_labels": {"value": True, "num_format": "0"},
        })
    index_chart.set_title({"name": "Price index by stock level (100 = commodity average)"})
    index_chart.set_legend({"position": "bottom"})
    ws.insert_chart("B23", index_chart, {"x_scale": 1.25})

    cv_grid = q2.pivot_table(index="market", columns="commodity", values="cv_pct")
    gap_grid = q5.pivot_table(index="market", columns="commodity", values="low_vs_high_pct")
    last = write_heatmap(ws, f, cv_grid, 22, 8, "Where prices swing the most (CV %)", f["heat"])
    write_heatmap(ws, f, gap_grid, last + 2, 8, "Low vs high stock price gap by market", f["heat_signed"])

    ws.write_url("B42", "internal:Explorer!A1", f["link"],
                 string="Open the Commodity Explorer to drill into one commodity")


def build_explorer(wb, ws, f, data, results):
    q1 = results["q1_price_by_commodity"]
    s1 = QUERY_SHEETS["q1_price_by_commodity"]
    price, commodity, market, stock, anomaly = (
        col_ref("Data", data, c)
        for c in ["purchase_price", "commodity", "market", "stock_level", "price_anomaly"]
    )
    markets = sorted(data["market"].dropna().unique())

    ws.hide_gridlines(2)
    ws.set_column("A:A", 2)
    ws.set_column("B:B", 24)
    ws.set_column("C:J", 13)
    ws.set_row(0, 28)
    ws.merge_range("B1:J1", "Commodity Explorer", f["title"])
    ws.merge_range("B2:J2", "Pick a commodity in the yellow cell. The table and chart recalculate with Excel formulas.",
                   f["subtitle"])

    ws.write("B4", "Commodity", f["label"])
    ws.write("C4", q1["commodity"].iloc[0], f["input"])
    ws.data_validation("C4", {"validate": "list", "source": "=" + col_ref(s1, q1, "commodity")})
    ws.write("B5", "Priced per", f["label"])
    ws.write_formula("C5", f'=INDEX({col_ref(s1, q1, "unit")},MATCH($C$4,{col_ref(s1, q1, "commodity")},0))')

    headers = ["Market", *STOCK_LEVELS, "Rows", "Avg price", "CV %", "Low vs high", "Anomaly share"]
    ws.write_row("B7", headers, f["header"])
    first = 7  # zero-based index of the first market row (Excel row 8)
    names = markets + ["All markets"]
    for i, name in enumerate(names):
        r = first + i
        n = r + 1  # Excel row number used inside formulas
        total = name == "All markets"
        by_market = "" if total else f",{market},$B{n}"
        mask = f"({commodity}=$C$4)" + ("" if total else f"*({market}=$B{n})")

        ws.write_string(r, 1, name, f["total"] if total else f["cell"])
        for j, level_col in enumerate(["C", "D", "E"]):
            ws.write_formula(r, 2 + j,
                             f'=IFERROR(AVERAGEIFS({price},{commodity},$C$4{by_market},{stock},{level_col}$7),"")',
                             f["price"])
        ws.write_formula(r, 5, f"=COUNTIFS({commodity},$C$4{by_market})", f["int"])
        ws.write_formula(r, 6, f'=IFERROR(AVERAGEIFS({price},{commodity},$C$4{by_market}),"")', f["price"])
        # Sample standard deviation for one commodity and market, divided by the average
        ws.write_formula(r, 7, f'=IFERROR(100*SQRT(SUMPRODUCT({mask}*({price}-G{n})^2)/(F{n}-1))/G{n},"")',
                         f["pct"])
        ws.write_formula(r, 8, f'=IFERROR(100*(C{n}/E{n}-1),"")', f["pct_signed"])
        ws.write_formula(r, 9, f'=IFERROR(100*AVERAGEIFS({anomaly},{commodity},$C$4{by_market}),"")', f["pct"])

    last_market = first + len(markets) - 1
    ws.conditional_format(first, 2, last_market, 4, HEAT)
    ws.conditional_format(first, 7, last_market, 7, {"type": "data_bar", "bar_color": STOCK_COLORS["High"]})
    ws.conditional_format(first, 9, last_market, 9, {"type": "data_bar", "bar_color": STOCK_COLORS["Low"]})

    caption_row = first + len(names) + 1
    ws.write_formula(caption_row, 1, '="Average "&$C$4&" price per "&$C$5&" by market and stock level"',
                     f["caption"])

    chart = wb.add_chart({"type": "column"})
    for j, level in enumerate(STOCK_LEVELS):
        chart.add_series({
            "name": level,
            "categories": ["Explorer", first, 1, last_market, 1],
            "values": ["Explorer", first, 2 + j, last_market, 2 + j],
            "fill": {"color": STOCK_COLORS[level]},
        })
    chart.set_title({"name": "=Explorer!" + xl_rowcol_to_cell(caption_row, 1, True, True),
                     "name_font": {"size": 12}})
    chart.set_legend({"position": "bottom"})
    chart.set_y_axis({"num_format": "#,##0"})
    ws.insert_chart(caption_row + 2, 1, chart, {"x_scale": 1.6, "y_scale": 1.2})


def build_notes(ws, f):
    ws.hide_gridlines(2)
    ws.set_column("A:A", 2)
    ws.set_column("B:B", 110)
    r = 0
    for kind, text in NOTES:
        if kind == "h":
            r += 1
            ws.write(r, 1, text, f["section"])
        else:
            ws.write(r, 1, text, f["note"])
        r += 1


def main() -> None:
    inputs = [CLEAN_FILE] + [OUT_DIR / f"{name}.csv" for name in QUERY_SHEETS]
    missing = [p.name for p in inputs if not p.exists()]
    if missing:
        raise SystemExit("Missing inputs, run steps 1 and 2 first: " + ", ".join(missing))

    data = pd.read_csv(CLEAN_FILE)
    results = {name: pd.read_csv(OUT_DIR / f"{name}.csv") for name in QUERY_SHEETS}

    DASHBOARD_FILE.parent.mkdir(exist_ok=True)
    wb = xlsxwriter.Workbook(str(DASHBOARD_FILE))
    f = make_formats(wb)

    # Tabs appear in the order they are added.
    dashboard = wb.add_worksheet("Dashboard")
    explorer = wb.add_worksheet("Explorer")

    q7_rows = 0
    for name, sheet in QUERY_SHEETS.items():
        ws = wb.add_worksheet(sheet)
        write_table(ws, results[name], f"tbl_{sheet}", number_formats(f, results[name]))
        ws.freeze_panes(1, 0)
        if name == "q7_price_index_stock_anomaly":
            q7_rows = write_q7_chart_data(ws, f, results[name])

    data_ws = wb.add_worksheet("Data")
    write_table(data_ws, data, "tbl_data", number_formats(f, data))
    data_ws.freeze_panes(1, 0)

    build_notes(wb.add_worksheet("Notes"), f)
    build_dashboard(wb, dashboard, f, data, results, q7_rows)
    build_explorer(wb, explorer, f, data, results)

    dashboard.activate()
    wb.close()
    print(f"Saved dashboard to {DASHBOARD_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
