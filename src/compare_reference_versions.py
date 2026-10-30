
from pathlib import Path

from src.extract import extract_data
from src.validate import validate_data
from src.transform import transform_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT / "data" / "input" / "sample_incoming.csv"
)

REFERENCE_FOLDER = PROJECT_ROOT / "data" / "reference"


def compare_versions():

    print("\n========== REFERENCE VERSION COMPARISON ==========")

    version_results = {}

    # Read incoming data once
    source_df = None

    for version in ["v1", "v2"]:

        reference_file = (
            REFERENCE_FOLDER / f"reference_{version}.csv"
        )

        # Extract incoming and reference data
        current_source, reference_df = extract_data(
            INPUT_FILE,
            reference_file
        )

        if source_df is None:
            source_df = current_source

        # Validate using selected reference version
        accepted_df, rejected_df = validate_data(
            current_source,
            reference_df
        )

        # Transform accepted records
        transformed_df = transform_data(
            accepted_df,
            reference_df,
            reference_version=version
        )

        version_results[version] = {
            "accepted": accepted_df,
            "rejected": rejected_df,
            "transformed": transformed_df,
        }

        print(f"\n--- Reference {version.upper()} ---")

        print("Reference records:", len(reference_df))
        print("Input records:", len(current_source))
        print("Accepted records:", len(accepted_df))
        print("Rejected records:", len(rejected_df))

    # Compare accepted event IDs
    v1_accepted = set(
        version_results["v1"]["accepted"]["event_id"]
    )

    v2_accepted = set(
        version_results["v2"]["accepted"]["event_id"]
    )

    newly_accepted = v2_accepted - v1_accepted
    no_longer_accepted = v1_accepted - v2_accepted

    print("\n========== VERSION CHANGE IMPACT ==========")

    print(
        "Newly accepted events in v2:",
        sorted(newly_accepted)
    )

    print(
        "Events no longer accepted in v2:",
        sorted(no_longer_accepted)
    )

    # Compare rejection reasons for changed events
    print("\n========== NEWLY ACCEPTED RECORD DETAILS ==========")

    v2_accepted_df = version_results["v2"]["accepted"]

    if newly_accepted:

        print(
            v2_accepted_df[
                v2_accepted_df["event_id"].isin(newly_accepted)
            ].to_string(index=False)
        )

    else:
        print("No newly accepted records.")

    print("\nReference version comparison completed!")


if __name__ == "__main__":
    compare_versions()
