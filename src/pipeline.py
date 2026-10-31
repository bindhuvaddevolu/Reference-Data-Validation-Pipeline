import argparse
import hashlib
import logging
import uuid

from datetime import datetime, timezone
from pathlib import Path

from src.extract import extract_data
from src.validate import validate_data
from src.transform import transform_data
from src.load import load_data, record_pipeline_failure


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT / "data" / "input" / "sample_incoming.csv"
)

REFERENCE_FOLDER = PROJECT_ROOT / "data" / "reference"

DATABASE_FILE = (
    PROJECT_ROOT / "data" / "output" / "reference_validation.db"
)

LOG_FILE = PROJECT_ROOT / "logs" / "pipeline.log"


def setup_logging():
    """Configure console and file logging."""

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ],
        force=True
    )


def run_pipeline(reference_version="v2"):
    """Execute the complete reference validation pipeline."""

    if reference_version not in ["v1", "v2"]:
        raise ValueError(
            "Reference version must be v1 or v2"
        )

    run_id = str(uuid.uuid4())

    start_time = datetime.now(timezone.utc).isoformat()

    logger = logging.getLogger(__name__)

    input_count = 0
    accepted_count = 0
    rejected_count = 0

    reference_file = (
        REFERENCE_FOLDER / f"reference_{reference_version}.csv"
    )

    try:

        logger.info("====================================")
        logger.info("PIPELINE STARTED")
        logger.info("Run ID: %s", run_id)
        logger.info("Input file: %s", INPUT_FILE.name)
        logger.info("Reference version: %s", reference_version)
        logger.info("Reference file: %s", reference_file.name)

        # STEP 1: EXTRACT
        logger.info("Step 1: Extracting data")

        source_df, reference_df = extract_data(
            INPUT_FILE,
            reference_file
        )

        input_count = len(source_df)

        # Hash the actual source file contents. This makes reject
        # deduplication stable across reruns, while detecting file changes.
        source_file_hash = hashlib.sha256(
            INPUT_FILE.read_bytes()
        ).hexdigest()

        logger.info("Input records: %s", input_count)
        logger.info("Reference records: %s", len(reference_df))
        logger.info("Source file SHA-256: %s", source_file_hash)

        # STEP 2: VALIDATE
        logger.info("Step 2: Validating data")

        accepted_df, rejected_df = validate_data(
            source_df,
            reference_df
        )

        accepted_count = len(accepted_df)
        rejected_count = len(rejected_df)

        logger.info("Accepted records: %s", accepted_count)
        logger.info("Rejected records: %s", rejected_count)

        # STEP 3: RECONCILIATION
        if input_count != accepted_count + rejected_count:

            raise ValueError(
                "Reconciliation failed: input count does not "
                "match accepted + rejected count"
            )

        logger.info("Record reconciliation successful")

        # STEP 4: TRANSFORM
        logger.info("Step 4: Transforming accepted records")

        transformed_df = transform_data(
            accepted_df,
            reference_df,
            reference_version=reference_version
        )

        if len(transformed_df) != accepted_count:
            raise ValueError(
                "Transformation count mismatch"
            )

        logger.info(
            "Transformed records: %s",
            len(transformed_df)
        )

        # STEP 5: LOAD
        logger.info("Step 5: Loading data into SQLite")

        result = load_data(
            transformed_df=transformed_df,
            rejected_df=rejected_df,
            db_path=DATABASE_FILE,
            run_id=run_id,
            source_file=INPUT_FILE.name,
            input_count=input_count,
            started_at=start_time,
            reference_version=reference_version,
            reference_file=reference_file.name,
            source_file_hash=source_file_hash
        )

        end_time = datetime.now(timezone.utc)

        duration = (
            end_time - datetime.fromisoformat(start_time)
        ).total_seconds()

        logger.info("====================================")
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("Run ID: %s", run_id)
        logger.info("Reference version: %s", reference_version)
        logger.info("Reference file: %s", reference_file.name)
        logger.info("Input records: %s", input_count)
        logger.info("Accepted records: %s", accepted_count)
        logger.info("Rejected records: %s", rejected_count)

        logger.info(
            "New accepted records inserted: %s",
            result["accepted_inserted"]
        )

        logger.info(
            "New rejected records inserted: %s",
            result["rejected_inserted"]
        )

        logger.info("Status: %s", result["status"])
        logger.info("Duration: %.2f seconds", duration)
        logger.info("====================================")

        return result

    except Exception as error:

        logger.exception(
            "PIPELINE FAILED | Run ID: %s",
            run_id
        )

        try:

            record_pipeline_failure(
                db_path=DATABASE_FILE,
                run_id=run_id,
                source_file=INPUT_FILE.name,
                start_time=start_time,
                error_message=str(error),
                input_count=input_count,
                accepted_count=accepted_count,
                rejected_count=rejected_count,
                reference_version=reference_version,
                reference_file=reference_file.name
            )

            logger.info(
                "Failure details saved in database"
            )

        except Exception:

            logger.exception(
                "Could not save failure audit record"
            )

        raise


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Reference Data Validation Pipeline"
    )

    parser.add_argument(
        "--reference-version",
        choices=["v1", "v2"],
        default="v2",
        help="Select reference dataset version"
    )

    args = parser.parse_args()

    setup_logging()

    run_pipeline(
        reference_version=args.reference_version
    )
