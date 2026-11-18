import json
from pathlib import Path

data_sample = [
    {"hour": 0, "price": 150.94},
    {"hour": 1, "price": 96.23},
    {"hour": 2, "price": 64.46},
    {"hour": 3, "price": 43.82},
    {"hour": 4, "price": None},
    {"hour": 5, "price": 44.76},
]

sample_path = Path("data/sample.json")
missing_path = Path("data/missing.json")

sample_path.parent.mkdir(exist_ok=True)

with open(sample_path, "w") as f:
    json.dump(data_sample, f, indent=2)


with open(sample_path) as f:
    loaded = json.load(f)

print(loaded)
print(loaded == data_sample)


try:
    with open(missing_path) as f:
        loaded2 = json.load(f)
except FileNotFoundError:
    print(f"File not found in {missing_path}")
