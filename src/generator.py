
import csv
import random
import argparse
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = ROOT / "data" / "input"
REFERENCE_DIR = ROOT / "data" / "reference"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42

INCOMING_FIELDS = [
    "event_id",
    "customer_id",
    "code",
    "event_date",
]

REFERENCE_FIELDS = [
    "code",
    "description",
    "valid_from",
    "valid_to",
    "status",
]


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def generate_reference_data():
    reference_v1 = [
        {
            "code": "HYD",
            "description": "Hyderabad",
            "valid_from": "2025-01-01",
            "valid_to": "9999-12-31",
            "status": "ACTIVE",
        },
        {
            "code": "BLR",
            "description": "Bengaluru",
            "valid_from": "2025-01-01",
            "valid_to": "9999-12-31",
            "status": "ACTIVE",
        },
        {
            "code": "CHN",
            "description": "Chennai",
            "valid_from": "2025-01-01",
            "valid_to": "9999-12-31",
            "status": "ACTIVE",
        },
        {
            "code": "OLD",
            "description": "Old Region",
            "valid_from": "2020-01-01",
            "valid_to": "2025-12-31",
            "status": "DEPRECATED",
        },
        {
            "code": "FUT",
            "description": "Future Region",
            "valid_from": "2027-01-01",
            "valid_to": "9999-12-31",
            "status": "ACTIVE",
        },
    ]

    # Version 2 retains old codes and introduces a new code.
    reference_v2 = [
        *reference_v1,
        {
            "code": "PNQ",
            "description": "Pune",
            "valid_from": "2026-01-01",
            "valid_to": "9999-12-31",
            "status": "ACTIVE",
        },
    ]

    write_csv(
        REFERENCE_DIR / "reference_v1.csv",
        REFERENCE_FIELDS,
        reference_v1,
    )

    write_csv(
        REFERENCE_DIR / "reference_v2.csv",
        REFERENCE_FIELDS,
        reference_v2,
    )

    print("Reference versions generated: v1 and v2")


def generate_sample_data():
    rows = [
        {
            "event_id": "E001",
            "customer_id": "C001",
            "code": "HYD",
            "event_date": "2026-10-20",
        },
        {
            "event_id": "E002",
            "customer_id": "C002",
            "code": "BLR",
            "event_date": "2026-10-21",
        },
        {
            "event_id": "E003",
            "customer_id": "C003",
            "code": "XYZ",
            "event_date": "2026-10-22",
        },
        {
            "event_id": "E004",
            "customer_id": "C004",
            "code": "OLD",
            "event_date": "2024-06-15",
        },
        {
            "event_id": "E005",
            "customer_id": "C005",
            "code": "OLD",
            "event_date": "2026-06-15",
        },
        {
            "event_id": "E006",
            "customer_id": "C006",
            "code": "FUT",
            "event_date": "2026-10-23",
        },
        {
            "event_id": "E007",
            "customer_id": "C007",
            "code": "PNQ",
            "event_date": "2026-10-24",
        },
        {
            "event_id": "E008",
            "customer_id": "",
            "code": "HYD",
            "event_date": "2026-10-25",
        },
        {
            "event_id": "E009",
            "customer_id": "C009",
            "code": "",
            "event_date": "2026-10-25",
        },
        {
            "event_id": "E010",
            "customer_id": "C010",
            "code": "CHN",
            "event_date": "not-a-date",
        },
        {
            "event_id": "E011",
            "customer_id": "C011",
            "code": "HYD",
            "event_date": "2026-10-26",
        },
        {
            "event_id": "E011",
            "customer_id": "C011",
            "code": "HYD",
            "event_date": "2026-10-26",
        },
    ]

    write_csv(
        INPUT_DIR / "sample_incoming.csv",
        INCOMING_FIELDS,
        rows,
    )

    print(f"Sample incoming data generated: {len(rows)} rows")


def generate_large_data(record_count):
    random.seed(SEED)

    codes = ["HYD", "BLR", "CHN", "OLD", "FUT", "PNQ"]

    start_date = date(2025, 1, 1)
    rows = []

    duplicate_count = record_count * 2 // 100
    missing_count = record_count * 2 // 100
    invalid_date_count = record_count * 2 // 100
    unknown_code_count = record_count * 2 // 100

    normal_count = (
        record_count
        - duplicate_count
        - missing_count
        - invalid_date_count
        - unknown_code_count
    )

    # 1. Generate normal records
    for i in range(1, normal_count + 1):
        event_date = start_date + timedelta(
            days=random.randint(0, 730)
        )

        rows.append({
            "event_id": f"EVT{i:07d}",
            "customer_id": f"CUST{random.randint(1, 20000):05d}",
            "code": random.choice(codes),
            "event_date": event_date.isoformat(),
        })

    # 2. Generate duplicate event IDs
    for i in range(duplicate_count):
        donor = rows[i % normal_count]

        rows.append({
            "event_id": donor["event_id"],
            "customer_id": f"CUST{random.randint(1, 20000):05d}",
            "code": random.choice(codes),
            "event_date": donor["event_date"],
        })

    # 3. Generate missing required fields
    for i in range(missing_count):
        rows.append({
            "event_id": f"MISSING{i:07d}",
            "customer_id": "",
            "code": random.choice(codes),
            "event_date": "2026-10-20",
        })

    # 4. Generate invalid dates
    for i in range(invalid_date_count):
        rows.append({
            "event_id": f"INVALID{i:07d}",
            "customer_id": f"CUST{random.randint(1, 20000):05d}",
            "code": random.choice(codes),
            "event_date": "not-a-date",
        })

    # 5. Generate unknown reference codes
    for i in range(unknown_code_count):
        rows.append({
            "event_id": f"UNKNOWN{i:07d}",
            "customer_id": f"CUST{random.randint(1, 20000):05d}",
            "code": "XYZ",
            "event_date": "2026-10-20",
        })

    random.shuffle(rows)

    write_csv(
        INPUT_DIR / f"large_incoming_{record_count}.csv",
        INCOMING_FIELDS,
        rows,
    )

    print(f"Large dataset generated: {record_count} rows")
    print(f"Random seed used: {SEED}")
    print(f"Normal records: {normal_count}")
    print(f"Duplicate records: {duplicate_count}")
    print(f"Missing-field records: {missing_count}")
    print(f"Invalid-date records: {invalid_date_count}")
    print(f"Unknown-code records: {unknown_code_count}")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate reproducible reference and incoming datasets"
    )

    parser.add_argument(
        "--size",
        type=int,
        default=100000,
        help="Number of records in large dataset",
    )

    args = parser.parse_args()

    if args.size < 1:
        parser.error("--size must be greater than zero")

    generate_reference_data()
    generate_sample_data()
    generate_large_data(args.size)

    print("All datasets generated successfully!")