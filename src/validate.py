
from datetime import date

import pandas as pd


REQUIRED_SOURCE_FIELDS = [
    "event_id",
    "customer_id",
    "code",
    "event_date",
]

SOURCE_COLUMNS_WITH_WARNING = [
    "source_row_number",
    "event_id",
    "customer_id",
    "code",
    "event_date",
    "validation_warning",
]

SOURCE_COLUMNS_WITH_REJECT = [
    "source_row_number",
    "event_id",
    "customer_id",
    "code",
    "event_date",
    "reject_reason",
]


def parse_date(value):
    """Convert ISO date string into Python date."""

    try:
        return date.fromisoformat(str(value).strip())
    except (ValueError, TypeError):
        return None


def validate_reference(reference_df):
    """Validate reference dataset before processing."""

    reference_lookup = {}

    for row in reference_df.itertuples(index=False):

        code = str(row.code).strip()
        description = str(row.description).strip()
        status = str(row.status).strip().upper()

        valid_from = parse_date(row.valid_from)
        valid_to = parse_date(row.valid_to)

        if not code:
            raise ValueError("Reference code cannot be empty")

        if not description:
            raise ValueError(
                f"Description missing for code: {code}"
            )

        if code in reference_lookup:
            raise ValueError(
                f"Duplicate reference code: {code}"
            )

        if valid_from is None or valid_to is None:
            raise ValueError(
                f"Invalid reference dates for code: {code}"
            )

        if valid_from > valid_to:
            raise ValueError(
                f"Invalid validity period for code: {code}"
            )

        if status not in ["ACTIVE", "DEPRECATED"]:
            raise ValueError(
                f"Invalid status for code: {code}"
            )

        reference_lookup[code] = {
            "description": description,
            "valid_from": valid_from,
            "valid_to": valid_to,
            "status": status,
        }

    return reference_lookup


def validate_data(source_df, reference_df):
    """
    Validate incoming records against reference data.

    Returns:
        accepted_df: Valid records with original source row numbers.
        rejected_df: Invalid records with rejection reasons.
    """

    reference_lookup = validate_reference(reference_df)

    accepted_records = []
    rejected_records = []

    # Identify all duplicate event IDs first.
    event_ids = (
        source_df["event_id"]
        .astype("string")
        .str.strip()
    )

    event_id_counts = event_ids.value_counts()

    duplicate_event_ids = set(
        event_id_counts[event_id_counts > 1].index
    )

    # Iterate through source records.
    for source_row_number, values in enumerate(
        source_df.itertuples(index=False, name=None),
        start=1
    ):

        row = dict(zip(source_df.columns, values))

        # Preserve original CSV data row number.
        row["source_row_number"] = source_row_number

        record = row.copy()

        reasons = []
        warning = ""

        # 1. Required field validation
        for field in REQUIRED_SOURCE_FIELDS:

            value = str(row[field]).strip()

            if not value:
                reasons.append(
                    f"MISSING_{field.upper()}"
                )

        # 2. Duplicate event ID validation
        event_id = str(row["event_id"]).strip()

        if event_id and event_id in duplicate_event_ids:
            reasons.append("DUPLICATE_EVENT_ID")

        # 3. Event date validation
        event_date = parse_date(row["event_date"])

        if (
            str(row["event_date"]).strip()
            and event_date is None
        ):
            reasons.append("INVALID_EVENT_DATE")

        # 4. Reference code validation
        code = str(row["code"]).strip()

        if code and code not in reference_lookup:

            reasons.append("UNKNOWN_CODE")

        elif code in reference_lookup and event_date is not None:

            reference = reference_lookup[code]

            # Check effective start date
            if event_date < reference["valid_from"]:

                reasons.append("NOT_YET_VALID")

            # Check effective end date
            elif event_date > reference["valid_to"]:

                reasons.append("EXPIRED_CODE")

            # Historical deprecated code
            elif reference["status"] == "DEPRECATED":

                warning = "HISTORICAL_DEPRECATED_CODE"

        # 5. Separate accepted and rejected records
        if reasons:

            record["reject_reason"] = "|".join(reasons)

            rejected_records.append(record)

        else:

            record["validation_warning"] = warning

            accepted_records.append(record)

    # Convert records into DataFrames.
    accepted_df = pd.DataFrame(
        accepted_records,
        columns=SOURCE_COLUMNS_WITH_WARNING
    )

    rejected_df = pd.DataFrame(
        rejected_records,
        columns=SOURCE_COLUMNS_WITH_REJECT
    )

    return accepted_df, rejected_df


if __name__ == "__main__":

    from pathlib import Path
    from src.extract import extract_data

    project_root = Path(__file__).resolve().parents[1]

    input_path = (
        project_root
        / "data"
        / "input"
        / "sample_incoming.csv"
    )

    reference_path = (
        project_root
        / "data"
        / "reference"
        / "reference_v2.csv"
    )

    source_df, reference_df = extract_data(
        input_path,
        reference_path
    )

    accepted_df, rejected_df = validate_data(
        source_df,
        reference_df
    )

    print("\n========== VALIDATION REPORT ==========")

    print("Total incoming records:", len(source_df))
    print("Accepted records:", len(accepted_df))
    print("Rejected records:", len(rejected_df))

    print("\n========== ACCEPTED RECORDS ==========")
    print(accepted_df.to_string(index=False))

    print("\n========== REJECTED RECORDS ==========")
    print(rejected_df.to_string(index=False))

    print("\n========== VALIDATION SUMMARY ==========")

    if not rejected_df.empty:
        print(
            rejected_df["reject_reason"]
            .value_counts()
            .to_string()
        )

    print("\nValidation completed successfully!")
