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
print(max_price)

min_price = min(row["price"] for row in valid_records)
print(min_price)

avg_price = sum(row["price"] for row in valid_records) / len(valid_records)

print(f"min: {min_price:.2f} max: {max_price:.2f} avg: {avg_price:.2f}")
