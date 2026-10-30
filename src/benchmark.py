
import time
from pathlib import Path

from src.extract import extract_data
from src.validate import validate_data
from src.transform import transform_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "input"
    / "large_incoming_100000.csv"
)

REFERENCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "reference_v2.csv"
)


def run_benchmark():

    start_time = time.perf_counter()

    # Step 1: Extract
    source_df, reference_df = extract_data(
        INPUT_FILE,
        REFERENCE_FILE
    )

    extraction_time = time.perf_counter()

    # Step 2: Validate
    accepted_df, rejected_df = validate_data(
        source_df,
        reference_df
    )

    validation_time = time.perf_counter()

    # Step 3: Transform
    transformed_df = transform_data(
        accepted_df,
        reference_df,
        reference_version="v2"
    )

    transformation_time = time.perf_counter()

    total_time = transformation_time - start_time

    print("\n========== PERFORMANCE REPORT ==========")

    print("Total input records:", len(source_df))
    print("Accepted records:", len(accepted_df))
    print("Rejected records:", len(rejected_df))
    print("Transformed records:", len(transformed_df))

    print("\nExtraction time: {:.4f} seconds".format(
        extraction_time - start_time
    ))

    print("Validation time: {:.4f} seconds".format(
        validation_time - extraction_time
    ))

    print("Transformation time: {:.4f} seconds".format(
        transformation_time - validation_time
    ))

    print("Total processing time: {:.4f} seconds".format(
        total_time
    ))

    if total_time > 0:
        print(
            "Processing throughput: {:.2f} records/second".format(
                len(source_df) / total_time
            )
        )

    print("\nPerformance benchmark completed!")


if __name__ == "__main__":
    run_benchmark()
