
from pathlib import Path

import pandas as pd


SOURCE_COLUMNS = [
    "event_id",
    "customer_id",
    "code",
    "event_date",
]

REFERENCE_COLUMNS = [
    "code",
    "description",
    "valid_from",
    "valid_to",
    "status",
]


def read_csv_with_schema(file_path, expected_columns):
    """Read a CSV file and verify its column names."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_csv(
            file_path,
            dtype="string",
            keep_default_na=False
        )
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=expected_columns)

    actual_columns = list(df.columns)

    if set(actual_columns) != set(expected_columns):
        missing = set(expected_columns) - set(actual_columns)
        unexpected = set(actual_columns) - set(expected_columns)

        raise ValueError(
            f"Schema mismatch in {file_path.name}. "
            f"Missing columns: {missing}. "
            f"Unexpected columns: {unexpected}"
        )

    return df[expected_columns]


def extract_data(input_path, reference_path):
    """Extract incoming records and reference records."""

    source_df = read_csv_with_schema(
        input_path,
        SOURCE_COLUMNS
    )

    reference_df = read_csv_with_schema(
        reference_path,
        REFERENCE_COLUMNS
    )

    return source_df, reference_df


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]

    input_path = (
        project_root / "data" / "input" / "sample_incoming.csv"
    )

    reference_path = (
        project_root / "data" / "reference" / "reference_v2.csv"
    )

    source_df, reference_df = extract_data(
        input_path,
        reference_path
    )

    print("Extraction successful!")
    print("Incoming records:", len(source_df))
    print("Reference records:", len(reference_df))
    print("\nIncoming columns:", list(source_df.columns))
    print("Reference columns:", list(reference_df.columns))
