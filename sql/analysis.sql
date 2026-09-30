-- Bangladesh commodity market: price analysis
-- Dialect: DuckDB. Run with: python src/02_run_queries.py
-- market_prices is the cleaned file data/processed/commodity_prices_clean.csv
-- Each query below is tagged with a name line that the runner uses as the output file name.
-- For PostgreSQL, cast before rounding, e.g. ROUND(AVG(purchase_price)::numeric, 2)


-- name: q1_price_by_commodity
-- Average, range and spread per commodity.
-- cv_pct (std dev / average) compares spread across items priced per kg and per litre.
SELECT
    commodity,
    unit,
    COUNT(*) AS observations,
    ROUND(AVG(purchase_price), 2) AS avg_price,
    ROUND(MIN(purchase_price), 2) AS min_price,
    ROUND(MAX(purchase_price), 2) AS max_price,
    ROUND(STDDEV_SAMP(purchase_price), 2) AS std_dev,
    ROUND(100 * STDDEV_SAMP(purchase_price) / AVG(purchase_price), 1) AS cv_pct
FROM market_prices
GROUP BY commodity, unit
ORDER BY cv_pct DESC, commodity;


-- name: q2_price_by_commodity_market
-- Average price and spread for every commodity and market pair.
SELECT
    commodity,
    market,
    COUNT(*) AS observations,
    ROUND(AVG(purchase_price), 2) AS avg_price,
    ROUND(STDDEV_SAMP(purchase_price), 2) AS std_dev,
    ROUND(100 * STDDEV_SAMP(purchase_price) / AVG(purchase_price), 1) AS cv_pct
FROM market_prices
GROUP BY commodity, market
ORDER BY commodity, avg_price DESC, market;


-- name: q3_price_by_stock_level
-- Core question: how does stock level relate to price for each commodity?
SELECT
    commodity,
    stock_level,
    stock_order,
    COUNT(*) AS observations,
    ROUND(AVG(purchase_price), 2) AS avg_price,
    ROUND(MIN(purchase_price), 2) AS min_price,
    ROUND(MAX(purchase_price), 2) AS max_price,
    ROUND(STDDEV_SAMP(purchase_price), 2) AS std_dev
FROM market_prices
GROUP BY commodity, stock_level, stock_order
ORDER BY commodity, stock_order;


-- name: q4_low_vs_high_stock_premium
-- One row per commodity: average price at each stock level and the low vs high gap.
WITH by_stock AS (
    SELECT
        commodity,
        AVG(CASE WHEN stock_level = 'Low' THEN purchase_price END) AS avg_low,
        AVG(CASE WHEN stock_level = 'Medium' THEN purchase_price END) AS avg_medium,
        AVG(CASE WHEN stock_level = 'High' THEN purchase_price END) AS avg_high
    FROM market_prices
    GROUP BY commodity
)
SELECT
    commodity,
    ROUND(avg_low, 2) AS avg_low,
    ROUND(avg_medium, 2) AS avg_medium,
    ROUND(avg_high, 2) AS avg_high,
    ROUND(avg_low - avg_high, 2) AS low_minus_high,
    ROUND(100 * (avg_low - avg_high) / avg_high, 1) AS low_vs_high_pct
FROM by_stock
ORDER BY low_vs_high_pct DESC, commodity;


-- name: q5_stock_premium_by_market
-- The same low vs high gap split by market. Check n_low and n_high first; some cells are small.
SELECT
    commodity,
    market,
    COUNT(CASE WHEN stock_level = 'Low' THEN 1 END) AS n_low,
    COUNT(CASE WHEN stock_level = 'High' THEN 1 END) AS n_high,
    ROUND(AVG(CASE WHEN stock_level = 'Low' THEN purchase_price END), 2) AS avg_low,
    ROUND(AVG(CASE WHEN stock_level = 'High' THEN purchase_price END), 2) AS avg_high,
    ROUND(
        100 * (AVG(CASE WHEN stock_level = 'Low' THEN purchase_price END)
             - AVG(CASE WHEN stock_level = 'High' THEN purchase_price END))
            / AVG(CASE WHEN stock_level = 'High' THEN purchase_price END),
        1
    ) AS low_vs_high_pct
FROM market_prices
GROUP BY commodity, market
ORDER BY commodity, low_vs_high_pct DESC NULLS LAST, market;


-- name: q6_anomaly_share_by_stock_level
-- How often each stock level produces a price anomaly (more than 15% above the median
-- price for the same variety and season), and how far prices sit from that median on average.
SELECT
    stock_level,
    COUNT(*) AS observations,
    COUNT(CASE WHEN price_anomaly = 1 THEN 1 END) AS anomaly_rows,
    ROUND(100.0 * AVG(price_anomaly), 1) AS anomaly_share_pct,
    ROUND(AVG(pct_vs_peer), 1) AS avg_pct_vs_peer
FROM market_prices
GROUP BY stock_level, stock_order
ORDER BY stock_order;


-- name: q7_price_index_stock_anomaly
-- Each price is indexed to its commodity average (100 = average) so all items share one scale.
-- Split by stock level and anomaly flag to see whether the low-stock premium is broad-based or driven by a few extreme purchases.
WITH indexed AS (
    SELECT
        stock_level,
        stock_order,
        price_anomaly,
        100 * purchase_price / AVG(purchase_price) OVER (PARTITION BY commodity) AS price_index
    FROM market_prices
)
SELECT
    stock_level,
    stock_order,
    price_anomaly,
    COUNT(*) AS observations,
    ROUND(AVG(price_index), 1) AS avg_price_index
FROM indexed
GROUP BY stock_level, stock_order, price_anomaly
ORDER BY stock_order, price_anomaly;


-- name: q8_weather_and_harvest
-- Price index (100 = commodity average) by weather and harvest season.
WITH indexed AS (
    SELECT
        weather,
        seasonal_harvest,
        100 * purchase_price / AVG(purchase_price) OVER (PARTITION BY commodity) AS price_index
    FROM market_prices
)
SELECT
    weather,
    seasonal_harvest,
    COUNT(*) AS observations,
    ROUND(AVG(price_index), 1) AS avg_price_index
FROM indexed
GROUP BY weather, seasonal_harvest
ORDER BY avg_price_index DESC, weather, seasonal_harvest;
