import heapq
from collections import defaultdict

# Drill 1: data types (SQL: column types)
zone = "10YLT-1001A0008Q"  # text -> VARCHAR
price = 85.3  # decimal -> FLOAT
hour = 14  # integer -> INT

print(zone, type(zone))
print(price, type(price))
print(hour, type(hour))

# Drill 2: slice text (SQL: SUBSTRING(zone, 4, 2))

print(zone[3:5])


# Drill 3: format output (SQL: FORMAT / CONCAT)

print(f"Hour {hour}: {price:.2f} EUR/MWh")

# Drill 4: build the prices table (SQL: CREATE TABLE + INSERT)

prices = [
    {"hour": 0, "price": 150.94},
    {"hour": 1, "price": 96.23},
    {"hour": 2, "price": 64.46},
    {"hour": 3, "price": 43.82},
    {"hour": 4, "price": None},
    {"hour": 5, "price": 44.76},
    {"hour": 6, "price": 48.83},
    {"hour": 7, "price": 51.23},
    {"hour": 8, "price": 64.81},
    {"hour": 9, "price": 71.39},
    {"hour": 10, "price": 83.75},
    {"hour": 11, "price": 94.23},
    {"hour": 12, "price": 103.90},
    {"hour": 13, "price": 123.45},
    {"hour": 14, "price": None},
    {"hour": 15, "price": 183.45},
    {"hour": 16, "price": 420.69},
    {"hour": 17, "price": 301.45},
    {"hour": 18, "price": 320.69},
    {"hour": 19, "price": 340.23},
    {"hour": 20, "price": 375.38},
    {"hour": 21, "price": 339.66},
    {"hour": 22, "price": 298.33},
    {"hour": 23, "price": 221.47},
]


# Drill 5: count rows (SQL: COUNT(*))

print(len(prices))

# Drill 6: print every row (SQL: SELECT *)

for row in prices:
    print(row["hour"], row["price"])

# Drill 7: one column as a list, loop version (SQL: SELECT price)

price_list = []

for row in prices:
    price_list.append(row["price"])

print(price_list)

# Drill 7.5: one column as a list, list comprehension (SQL: SELECT price)

price_list2 = [row["price"] for row in prices]
print(price_list2)

# Drill 8: filter rows, None check first (SQL: SELECT * WHERE price > 100)

expensive_hours = [
    row for row in prices if row["price"] is not None and row["price"] > 100
]
print(expensive_hours)

# Drill 9: count non-NULL prices, len() and sum() versions (SQL: COUNT(price))

valid_record_count = len([row for row in prices if row["price"] is not None])
print(valid_record_count)

valid_record_count2 = sum(1 for row in prices if row["price"] is not None)
print(valid_record_count2)

# Drill 9.5: sum non-NULL prices (SQL: SUM(price))
valid_price_sum = sum(row["price"] for row in prices if row["price"] is not None)
print(valid_price_sum)


# Drill 10: Min, max and avg non-NULL prices (SQL: MIN, MAX, AVG)

valid_records = [row for row in prices if row["price"] is not None]

max_price = max(row["price"] for row in valid_records)
min_price = min(row["price"] for row in valid_records)
avg_price = sum(row["price"] for row in valid_records) / len(valid_records)

print(f"min: {min_price:.2f} max: {max_price:.2f} avg: {avg_price:.2f}")

# Drill 11: Nulls to 0's in expressional condition (SQL: COALESCE(x,0))
prices_no_nulls = [
    {"hour": row["hour"], "price": 0.0 if row["price"] is None else row["price"]}
    for row in prices
]
print(prices_no_nulls)
print(prices[4])

# Drill 12: Custom column creation (SQL: CASE)

prices_with_periods = [
    {**row, "period": "peak" if 8 <= row["hour"] <= 19 else "off-peak"}
    for row in prices
]
print(prices_with_periods)

# Drill 13: List sorting (SQL: TOP *)

highest_3_prices = sorted(
    (row for row in prices if row["price"] is not None),
    key=lambda row: row["price"],
    reverse=True,
)[:3]

print(highest_3_prices)

# Drill 13: List sorting heapq.nlargest (SQL: TOP *)
highest_3_prices2 = heapq.nlargest(
    3,
    (row for row in prices if row["price"] is not None),
    key=lambda row: row["price"],
)

print(highest_3_prices2)

# Drill 14: Average price per period (SQL: Group by)

rows_by_period = defaultdict(list)
for row in prices_with_periods:
    if row["price"] is not None:
        rows_by_period[row["period"]].append(row["price"])

for period, period_prices in rows_by_period.items():
    print(period, round(sum(period_prices) / len(period_prices), 2))

# Drill 15: creating sets (SQL: DISTINCT)

unique_periods = {row["period"] for row in prices_with_periods}
print(unique_periods)

# Drill 16: dict join (SQL: LEFT JOIN)

temps = {
    0: -2.3,
    1: -0.7,
    2: 0.5,
    3: 1.4,
    4: 2.8,
    10: 7.2,
}

prices_with_temperature = [
    {**row, "temperature": temps.get(row["hour"])} for row in prices
]
print(prices_with_temperature)

# Drill 17: average function (SQL: UDF)


def avg_price_per_period(hourly_prices, start_hour, end_hour):
    filtered_hourly_prices = [
        row
        for row in hourly_prices
        if start_hour <= row["hour"] <= end_hour and row["price"] is not None
    ]

    if len(filtered_hourly_prices):
        return sum(row["price"] for row in filtered_hourly_prices) / len(
            filtered_hourly_prices
        )
    else:
        return (
            None  # no valid prices in range -> "no data", like SQL AVG returning NULL
        )


for start, end in [(8, 19), (1, 10), (4, 4)]:
    avg = avg_price_per_period(prices, start, end)
    shown = "no data" if avg is None else f"{avg:.2f}"
    print(f"avg hours {start}-{end}: {shown}")

# Drill 17.5: max per variation (SQL: UDF)


def max_price_per_period(hourly_prices, start_hour, end_hour):
    max_hourly_price = max(
        [
            row["price"]
            for row in hourly_prices
            if start_hour <= row["hour"] <= end_hour and row["price"] is not None
        ],
        default=None,
    )

    return max_hourly_price


for start, end in [(8, 19), (1, 10), (4, 4)]:
    max_p = max_price_per_period(prices, start, end)
    shown = "no data" if max_p is None else f"{max_p:.2f}"
    print(f"max hours {start}-{end}: {shown}")

# Drill 18: first hour where price >150 (SQL: TOP 1 WHERE CLAUSE)


def first_hour_above(threshold, hourly_prices, start_hour, end_hour):
    first_hour_above_threshold = next(
        (
            row["hour"]
            for row in hourly_prices
            if row["price"] is not None
            and start_hour <= row["hour"] <= end_hour
            and row["price"] > threshold
        ),
        None,
    )

    return first_hour_above_threshold


threshold = 150.0
for start, end in [(4, 18), (17, 23), (2, 5), (6, 7), (23, 23)]:
    hour = first_hour_above(threshold, prices, start, end)
    shown = f"none above {threshold}" if hour is None else hour
    print(f"hours {start} - {end} : {shown}")

# Drill 19: hourly delta calculations by looping and remembering previous row (SQL: LAG usage)


def hourly_delta_price_change(hourly_prices, start_hour, end_hour):
    previous_hour_price = None
    filtered_price_range = (
        row for row in hourly_prices if start_hour <= row["hour"] <= end_hour
    )

    result = []

    for row in filtered_price_range:
        current_price = row["price"]

        if current_price is not None and previous_hour_price is not None:
            delta = current_price - previous_hour_price
        else:
            delta = None

        result.append({"hour": row["hour"], "price_delta": delta})

        previous_hour_price = current_price

    return result


def price_format(price):
    if price is not None:
        return f"{price:.2f}"
    else:
        return "n/a"


returned_result = hourly_delta_price_change(prices, 0, 23)

for row in returned_result:
    print(f"hour: {row["hour"]:<2} delta_price: {price_format(row["price_delta"]):>7}")

# Drill 20: running total calculation (SQL: SUM(price) OVER (ORDER by hour))


def running_total_in_period(hourly_prices, start_hour, end_hour):
    running_total = 0
    filtered_prices = (row for row in hourly_prices if start_hour <= row["hour"] <= end_hour)

    result = []

    for row in filtered_prices:
        if row["price"] is not None:
            running_total += row["price"]

        result.append({"hour": row["hour"], "running_total": running_total})

    return result


returned_result2 = running_total_in_period(prices, 0, 23)

for row in returned_result2:
    print(f"hour: {row["hour"]:<2} running_total: {price_format(row["running_total"]):>7}")
