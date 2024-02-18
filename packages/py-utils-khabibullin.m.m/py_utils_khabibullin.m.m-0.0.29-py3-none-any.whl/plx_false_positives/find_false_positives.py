import json
from prettytable import PrettyTable

def print_false_positives(file: str):
    table = PrettyTable(["Id", "deal value", "text"])

    with open(file) as f:
        data = json.load(f)
        mismatches = data["mismatches"]
        for item in mismatches:
            if item["deal_value"] is not None:
                table.add_row([item["id"], item["deal_value"], item["text"]])


    print(f"Count of items: {len(data)}")
    print(table)
