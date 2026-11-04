import csv

def summarize(path):
    result = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            group = row["group"]
            value = float(row["value"])
            result[group] = result.get(group, 0) + value
    return result
