# SQL results

Output of the queries in sql/analysis.sql. Regenerate with python src/02_run_queries.py.

## q1_price_by_commodity

Average, range and spread per commodity. cv_pct (std dev / average) compares spread across items priced per kg and per litre.

| commodity   | unit   |   observations |   avg_price |   min_price |   max_price |   std_dev |   cv_pct |
|:------------|:-------|---------------:|------------:|------------:|------------:|----------:|---------:|
| Onion       | Kg     |            311 |       85.88 |       45.09 |         120 |     15.49 |     18   |
| Garlic      | Kg     |            264 |      157.53 |      100    |         200 |     21.11 |     13.4 |
| Potato      | Kg     |            322 |       31.35 |       20    |          40 |      4.21 |     13.4 |
| Edible Oil  | L      |            279 |      170.63 |      123.95 |         200 |     18.71 |     11   |
| Rice        | Kg     |            412 |       67.97 |       50    |          80 |      7.32 |     10.8 |
| Lentil      | Kg     |            312 |      121.93 |       91.21 |         140 |     12.3  |     10.1 |

## q2_price_by_commodity_market

Average price and spread for every commodity and market pair.

| commodity   | market               |   observations |   avg_price |   std_dev |   cv_pct |
|:------------|:---------------------|---------------:|------------:|----------:|---------:|
| Edible Oil  | Khulna               |             36 |      174    |     17.2  |      9.9 |
| Edible Oil  | Barishal             |             22 |      173.01 |     12.9  |      7.5 |
| Edible Oil  | Chattogram           |             56 |      172.19 |     21.06 |     12.2 |
| Edible Oil  | Sylhet               |             40 |      171.19 |     20.41 |     11.9 |
| Edible Oil  | Karwan Bazar (Dhaka) |             72 |      169.52 |     18.77 |     11.1 |
| Edible Oil  | Rajshahi             |             53 |      166.79 |     17.67 |     10.6 |
| Garlic      | Rajshahi             |             37 |      162.62 |     24.24 |     14.9 |
| Garlic      | Barishal             |             27 |      160.79 |     18.26 |     11.4 |
| Garlic      | Khulna               |             45 |      156.88 |     19.18 |     12.2 |
| Garlic      | Karwan Bazar (Dhaka) |             76 |      156.45 |     22.43 |     14.3 |
| Garlic      | Chattogram           |             51 |      155.94 |     19.85 |     12.7 |
| Garlic      | Sylhet               |             28 |      154.54 |     21.08 |     13.6 |
| Lentil      | Chattogram           |             67 |      124.45 |     11.73 |      9.4 |
| Lentil      | Sylhet               |             35 |      123.48 |     12.67 |     10.3 |
| Lentil      | Rajshahi             |             53 |      123.05 |     12.22 |      9.9 |
| Lentil      | Barishal             |             29 |      120.29 |     13.18 |     11   |
| Lentil      | Karwan Bazar (Dhaka) |             74 |      120.28 |     11.74 |      9.8 |
| Lentil      | Khulna               |             54 |      119.85 |     12.86 |     10.7 |
| Onion       | Chattogram           |             66 |       87.77 |     14.57 |     16.6 |
| Onion       | Sylhet               |             33 |       86.53 |     14.45 |     16.7 |
| Onion       | Rajshahi             |             58 |       86.11 |     14.9  |     17.3 |
| Onion       | Barishal             |             32 |       85.34 |     17.81 |     20.9 |
| Onion       | Karwan Bazar (Dhaka) |             78 |       84.92 |     16.18 |     19.1 |
| Onion       | Khulna               |             44 |       84.35 |     15.87 |     18.8 |
| Potato      | Khulna               |             47 |       31.88 |      4.34 |     13.6 |
| Potato      | Barishal             |             29 |       31.74 |      4.49 |     14.1 |
| Potato      | Karwan Bazar (Dhaka) |             87 |       31.46 |      4.07 |     12.9 |
| Potato      | Chattogram           |             68 |       31.23 |      4.17 |     13.4 |
| Potato      | Rajshahi             |             56 |       31.18 |      4.21 |     13.5 |
| Potato      | Sylhet               |             35 |       30.5  |      4.35 |     14.3 |
| Rice        | Karwan Bazar (Dhaka) |            107 |       68.41 |      8.08 |     11.8 |
| Rice        | Khulna               |             64 |       68.35 |      7.21 |     10.5 |
| Rice        | Chattogram           |             91 |       68.13 |      7.23 |     10.6 |
| Rice        | Sylhet               |             48 |       68.09 |      6.4  |      9.4 |
| Rice        | Barishal             |             38 |       67.31 |      7.39 |     11   |
| Rice        | Rajshahi             |             64 |       66.93 |      6.98 |     10.4 |

## q3_price_by_stock_level

Core question: how does stock level relate to price for each commodity?

| commodity   | stock_level   |   stock_order |   observations |   avg_price |   min_price |   max_price |   std_dev |
|:------------|:--------------|--------------:|---------------:|------------:|------------:|------------:|----------:|
| Edible Oil  | Low           |             1 |             64 |      187.3  |      144    |      200    |     14.02 |
| Edible Oil  | Medium        |             2 |            148 |      169.01 |      130.4  |      200    |     16.23 |
| Edible Oil  | High          |             3 |             67 |      158.28 |      123.95 |      192.86 |     16.43 |
| Garlic      | Low           |             1 |             46 |      172.6  |      137.28 |      200    |     18.84 |
| Garlic      | Medium        |             2 |            159 |      156.56 |      100    |      200    |     20.2  |
| Garlic      | High          |             3 |             59 |      148.4  |      112.67 |      197.63 |     19.13 |
| Lentil      | Low           |             1 |             67 |      132.16 |      112.81 |      140    |      8.03 |
| Lentil      | Medium        |             2 |            178 |      120.93 |       94.61 |      140    |     11.58 |
| Lentil      | High          |             3 |             67 |      114.37 |       91.21 |      139.68 |     11.07 |
| Onion       | Low           |             1 |             78 |       91.89 |       46.18 |      120    |     15.99 |
| Onion       | Medium        |             2 |            160 |       84.38 |       51.76 |      120    |     14.89 |
| Onion       | High          |             3 |             73 |       82.73 |       45.09 |      115.71 |     14.69 |
| Potato      | Low           |             1 |             61 |       34.24 |       24.08 |       40    |      3.89 |
| Potato      | Medium        |             2 |            169 |       31.14 |       20.92 |       40    |      3.94 |
| Potato      | High          |             3 |             92 |       29.8  |       20    |       40    |      3.98 |
| Rice        | Low           |             1 |             92 |       73.95 |       54.56 |       80    |      5.97 |
| Rice        | Medium        |             2 |            236 |       67.38 |       50    |       80    |      6.65 |
| Rice        | High          |             3 |             84 |       63.09 |       50    |       78.4  |      6.02 |

## q4_low_vs_high_stock_premium

One row per commodity: average price at each stock level and the low vs high gap.

| commodity   |   avg_low |   avg_medium |   avg_high |   low_minus_high |   low_vs_high_pct |
|:------------|----------:|-------------:|-----------:|-----------------:|------------------:|
| Edible Oil  |    187.3  |       169.01 |     158.28 |            29.02 |              18.3 |
| Rice        |     73.95 |        67.38 |      63.09 |            10.86 |              17.2 |
| Garlic      |    172.6  |       156.56 |     148.4  |            24.2  |              16.3 |
| Lentil      |    132.16 |       120.93 |     114.37 |            17.78 |              15.5 |
| Potato      |     34.24 |        31.14 |      29.8  |             4.44 |              14.9 |
| Onion       |     91.89 |        84.38 |      82.73 |             9.16 |              11.1 |

## q5_stock_premium_by_market

The same low vs high gap split by market. Check n_low and n_high first; some cells are small.

| commodity   | market               |   n_low |   n_high |   avg_low |   avg_high |   low_vs_high_pct |
|:------------|:---------------------|--------:|---------:|----------:|-----------:|------------------:|
| Edible Oil  | Sylhet               |       8 |       13 |    196.39 |     158.86 |              23.6 |
| Edible Oil  | Rajshahi             |      10 |        8 |    185.38 |     152.59 |              21.5 |
| Edible Oil  | Karwan Bazar (Dhaka) |      17 |       15 |    184.79 |     154.99 |              19.2 |
| Edible Oil  | Khulna               |      10 |       12 |    188.49 |     159.71 |              18   |
| Edible Oil  | Chattogram           |      15 |       14 |    188.69 |     161.18 |              17.1 |
| Edible Oil  | Barishal             |       4 |        5 |    176.47 |     164.21 |               7.5 |
| Garlic      | Sylhet               |       2 |        5 |    182.98 |     138.56 |              32.1 |
| Garlic      | Rajshahi             |       6 |        7 |    189.05 |     154.95 |              22   |
| Garlic      | Chattogram           |       8 |       12 |    173.91 |     143.91 |              20.8 |
| Garlic      | Karwan Bazar (Dhaka) |      19 |       18 |    170.53 |     149.3  |              14.2 |
| Garlic      | Barishal             |       3 |        7 |    174.62 |     154.39 |              13.1 |
| Garlic      | Khulna               |       8 |       10 |    160.52 |     148.3  |               8.2 |
| Lentil      | Sylhet               |       9 |        7 |    133.08 |     110.62 |              20.3 |
| Lentil      | Khulna               |       8 |       13 |    130.16 |     110.73 |              17.5 |
| Lentil      | Barishal             |       4 |        8 |    136.35 |     117.48 |              16.1 |
| Lentil      | Karwan Bazar (Dhaka) |      15 |       18 |    130.81 |     113.32 |              15.4 |
| Lentil      | Rajshahi             |      10 |       11 |    133.18 |     117.31 |              13.5 |
| Lentil      | Chattogram           |      21 |       10 |    132.2  |     117.92 |              12.1 |
| Onion       | Barishal             |       5 |       10 |    106.93 |      83.14 |              28.6 |
| Onion       | Rajshahi             |      14 |       10 |     93.66 |      80.9  |              15.8 |
| Onion       | Chattogram           |      17 |       14 |     90.42 |      81.21 |              11.3 |
| Onion       | Karwan Bazar (Dhaka) |      20 |       22 |     89.76 |      82.26 |               9.1 |
| Onion       | Khulna               |      12 |       13 |     91.01 |      84.2  |               8.1 |
| Onion       | Sylhet               |      10 |        4 |     89.74 |      89.46 |               0.3 |
| Potato      | Rajshahi             |      11 |       21 |     35.49 |      28.61 |              24   |
| Potato      | Khulna               |       7 |       14 |     33.82 |      29.06 |              16.4 |
| Potato      | Sylhet               |       7 |        8 |     33.62 |      29.12 |              15.5 |
| Potato      | Karwan Bazar (Dhaka) |      19 |       25 |     34.41 |      30.05 |              14.5 |
| Potato      | Chattogram           |      11 |       18 |     34.56 |      31.04 |              11.3 |
| Potato      | Barishal             |       6 |        6 |     32.07 |      31.87 |               0.6 |
| Rice        | Barishal             |       8 |        8 |     77.02 |      61.48 |              25.3 |
| Rice        | Chattogram           |      19 |       25 |     73.69 |      63.03 |              16.9 |
| Rice        | Rajshahi             |      13 |       13 |     72.92 |      62.44 |              16.8 |
| Rice        | Khulna               |      12 |       13 |     74.27 |      63.79 |              16.4 |
| Rice        | Karwan Bazar (Dhaka) |      34 |       16 |     73.61 |      63.38 |              16.1 |
| Rice        | Sylhet               |       6 |        9 |     74.26 |      64.1  |              15.8 |

## q6_anomaly_share_by_stock_level

How often each stock level produces a price anomaly (more than 15% above the median price for the same variety and season), and how far prices sit from that median on average.

| stock_level   |   observations |   anomaly_rows |   anomaly_share_pct |   avg_pct_vs_peer |
|:--------------|---------------:|---------------:|--------------------:|------------------:|
| Low           |            408 |            118 |                28.9 |               8.5 |
| Medium        |           1050 |             86 |                 8.2 |              -0.7 |
| High          |            442 |             28 |                 6.3 |              -5.3 |

## q7_price_index_stock_anomaly

Each price is indexed to its commodity average (100 = average) so all items share one scale. Split by stock level and anomaly flag to see whether the low-stock premium is broad-based or driven by a few extreme purchases.

| stock_level   |   stock_order |   price_anomaly |   observations |   avg_price_index |
|:--------------|--------------:|----------------:|---------------:|------------------:|
| Low           |             1 |               0 |            290 |             104.3 |
| Low           |             1 |               1 |            118 |             119.6 |
| Medium        |             2 |               0 |            964 |              97.2 |
| Medium        |             2 |               1 |             86 |             119.9 |
| High          |             3 |               0 |            414 |              92.5 |
| High          |             3 |               1 |             28 |             119.7 |

## q8_weather_and_harvest

Price index (100 = commodity average) by weather and harvest season.

| weather   | seasonal_harvest   |   observations |   avg_price_index |
|:----------|:-------------------|---------------:|------------------:|
| Flood     | No                 |             65 |             113.6 |
| Flood     | Yes                |             38 |             109.4 |
| Rainy     | No                 |            474 |             106.7 |
| Sunny     | No                 |            572 |             101.8 |
| Rainy     | Yes                |            300 |              95.9 |
| Sunny     | Yes                |            451 |              90.7 |
