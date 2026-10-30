
import pandas as pd


def transform_data(
    accepted_df,
    reference_df,
    reference_version="v2"
):
    """
    Enrich accepted records with reference information
    and prepare them for target publishing.

    Preserves original source row numbers for traceability.
    """

    # Work on a copy to avoid modifying original data.
    transformed_df = accepted_df.copy()

    # Handle empty input.
    if transformed_df.empty:

        output_columns = [
            "source_row_number",
            "event_id",
            "customer_id",
            "code",
            "description",
            "event_date",
            "reference_status",
            "reference_version",
            "event_year",
            "event_month",
            "validation_warning",
        ]

        return pd.DataFrame(columns=output_columns)

    # Prepare reference lookup.
    reference = reference_df.copy()

    reference["code"] = (
        reference["code"]
        .astype(str)
        .str.strip()
    )

    reference["status"] = (
        reference["status"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Create lookup dictionaries.
    description_lookup = dict(
        zip(reference["code"], reference["description"])
    )

    status_lookup = dict(
        zip(reference["code"], reference["status"])
    )

    # Add reference description.
    transformed_df["description"] = (
        transformed_df["code"]
        .astype(str)
        .str.strip()
        .map(description_lookup)
    )

    # Add reference status.
    transformed_df["reference_status"] = (
        transformed_df["code"]
        .astype(str)
        .str.strip()
        .map(status_lookup)
    )

    # Add reference version.
    transformed_df["reference_version"] = reference_version

    # Derive event year and month.
    event_dates = pd.to_datetime(
        transformed_df["event_date"],
        format="%Y-%m-%d",
        errors="raise"
    )

    transformed_df["event_year"] = event_dates.dt.year
    transformed_df["event_month"] = event_dates.dt.month

    # Ensure warning column exists.
    if "validation_warning" not in transformed_df.columns:
        transformed_df["validation_warning"] = ""

    # Ensure source row number exists.
    if "source_row_number" not in transformed_df.columns:
        raise ValueError(
            "source_row_number missing from accepted records"
        )

    # Define target column order.
    target_columns = [
        "source_row_number",
        "event_id",
        "customer_id",
        "code",
        "description",
        "event_date",
        "reference_status",
        "reference_version",
        "event_year",
        "event_month",
        "validation_warning",
    ]

    transformed_df = transformed_df[target_columns]

    return transformed_df


if __name__ == "__main__":

    from pathlib import Path

    from src.extract import extract_data
    from src.validate import validate_data

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

    # Extract.
    source_df, reference_df = extract_data(
        input_path,
        reference_path
    )

    # Validate.
    accepted_df, rejected_df = validate_data(
        source_df,
        reference_df
    )

    # Transform accepted records.
    transformed_df = transform_data(
        accepted_df,
        reference_df,
        reference_version="v2"
    )

    # Save transformed output.
    output_path = (
        project_root
        / "data"
        / "output"
    )

    output_path.mkdir(parents=True, exist_ok=True)

    transformed_df.to_csv(
        output_path / "transformed_data.csv",
        index=False
    )

    print("\n========== TRANSFORMATION REPORT ==========")

    print("Accepted records:", len(accepted_df))
    print("Transformed records:", len(transformed_df))

    print("\n========== TRANSFORMED DATA ==========")

    print(transformed_df.to_string(index=False))

    print("\nTransformed file saved successfully!")
