import hashlib
import sqlite3

from datetime import datetime, timezone
from pathlib import Path


def create_tables(connection):
    """Create target, quarantine and pipeline audit tables."""

    cursor = connection.cursor()

    # 1. Accepted records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accepted_records (
            event_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT,
            event_date TEXT NOT NULL,
            reference_status TEXT,
            reference_version TEXT NOT NULL,
            event_year INTEGER,
            event_month INTEGER,
            validation_warning TEXT,
            source_file TEXT,
            source_row_number INTEGER,
            run_id TEXT NOT NULL,
            loaded_at TEXT NOT NULL,
            PRIMARY KEY (event_id, reference_version)
        )
    """)

    # 2. Rejected records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rejected_records (
            run_id TEXT NOT NULL,
            source_row_number INTEGER NOT NULL,
            event_id TEXT,
            customer_id TEXT,
            code TEXT,
            event_date TEXT,
            reject_reason TEXT,
            source_file TEXT,
            rejected_at TEXT NOT NULL,
            PRIMARY KEY (run_id, source_row_number)
        )
    """)

    # 3. Pipeline execution audit table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id TEXT PRIMARY KEY,
            source_file TEXT,
            reference_version TEXT,
            reference_file TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT,
            input_count INTEGER,
            accepted_count INTEGER,
            rejected_count INTEGER,
            error_message TEXT
        )
    """)

    # 4. Backward-compatible database migration.
    # Add new columns if pipeline_runs already existed.

    existing_columns = {
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(pipeline_runs)"
        ).fetchall()
    }

    if "reference_version" not in existing_columns:
        cursor.execute("""
            ALTER TABLE pipeline_runs
            ADD COLUMN reference_version TEXT
        """)

    if "reference_file" not in existing_columns:
        cursor.execute("""
            ALTER TABLE pipeline_runs
            ADD COLUMN reference_file TEXT
        """)

    # 5. Backward-compatible rejected-record idempotency migration.
    rejected_columns = {
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(rejected_records)"
        ).fetchall()
    }

    if "source_file_hash" not in rejected_columns:
        cursor.execute("""
            ALTER TABLE rejected_records
            ADD COLUMN source_file_hash TEXT
        """)

    if "reference_version" not in rejected_columns:
        cursor.execute("""
            ALTER TABLE rejected_records
            ADD COLUMN reference_version TEXT
        """)

    # Legacy rows keep NULL hashes and remain preserved.
    # New rows are unique per file content, source row and reference version.
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        uq_rejected_source_row_version
        ON rejected_records (
            source_file_hash,
            source_row_number,
            reference_version
        )
        WHERE source_file_hash IS NOT NULL
          AND reference_version IS NOT NULL
    """)

    connection.commit()


def record_pipeline_failure(
    db_path,
    run_id,
    source_file,
    start_time,
    error_message,
    input_count=0,
    accepted_count=0,
    rejected_count=0,
    reference_version=None,
    reference_file=None,
    source_file_hash=None
):
    """Record a failed pipeline execution independently."""

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    try:
        create_tables(connection)

        end_time = datetime.now(timezone.utc).isoformat()

        connection.execute("""
            INSERT INTO pipeline_runs (
                run_id,
                source_file,
                reference_version,
                reference_file,
                start_time,
                end_time,
                status,
                input_count,
                accepted_count,
                rejected_count,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(run_id) DO UPDATE SET
                source_file = excluded.source_file,
                reference_version = excluded.reference_version,
                reference_file = excluded.reference_file,
                end_time = excluded.end_time,
                status = excluded.status,
                input_count = excluded.input_count,
                accepted_count = excluded.accepted_count,
                rejected_count = excluded.rejected_count,
                error_message = excluded.error_message
        """, (
            run_id,
            source_file,
            reference_version,
            reference_file,
            start_time,
            end_time,
            "FAILED",
            input_count,
            accepted_count,
            rejected_count,
            str(error_message)[:2000]
        ))

        connection.commit()

    finally:
        connection.close()


def load_data(
    transformed_df,
    rejected_df,
    db_path,
    run_id,
    source_file,
    input_count,
    started_at=None,
    reference_version=None,
    reference_file=None,
    source_file_hash=None
):
    """
    Load accepted and rejected records into SQLite.

    Accepted records:
        Idempotent using event_id + reference_version.

    Rejected records:
        Idempotent using source_file_hash + source_row_number
        + reference_version. run_id remains execution audit metadata.

    Pipeline audit:
        Stores source file, reference version and reference filename.

    All data changes within this load are transactional.
    """

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    start_time = (
        started_at
        or datetime.now(timezone.utc).isoformat()
    )

    accepted_inserted = 0
    rejected_inserted = 0

    # Direct callers that do not provide a content hash get a stable
    # fallback based on the source filename. The main pipeline passes
    # the SHA-256 hash of the actual input file contents.
    if source_file_hash is None:
        source_file_hash = hashlib.sha256(
            str(source_file).encode("utf-8")
        ).hexdigest()

    try:
        create_tables(connection)

        cursor = connection.cursor()

        cursor.execute("BEGIN")

        loaded_at = datetime.now(timezone.utc).isoformat()

        # 1. Load accepted records
        for row_number, (_, row) in enumerate(
            transformed_df.iterrows(),
            start=1
        ):

            source_row_number = int(
                row.get("source_row_number", row_number)
            )

            cursor.execute("""
                INSERT OR IGNORE INTO accepted_records (
                    event_id,
                    customer_id,
                    code,
                    description,
                    event_date,
                    reference_status,
                    reference_version,
                    event_year,
                    event_month,
                    validation_warning,
                    source_file,
                    source_row_number,
                    run_id,
                    loaded_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["event_id"],
                row["customer_id"],
                row["code"],
                row["description"],
                row["event_date"],
                row["reference_status"],
                row["reference_version"],
                int(row["event_year"]),
                int(row["event_month"]),
                row["validation_warning"],
                source_file,
                source_row_number,
                run_id,
                loaded_at
            ))

            accepted_inserted += cursor.rowcount

        # 2. Load rejected records
        rejected_at = datetime.now(timezone.utc).isoformat()

        for row_number, (_, row) in enumerate(
            rejected_df.iterrows(),
            start=1
        ):

            source_row_number = int(
                row.get("source_row_number", row_number)
            )

            cursor.execute("""
                INSERT OR IGNORE INTO rejected_records (
                    run_id,
                    source_row_number,
                    event_id,
                    customer_id,
                    code,
                    event_date,
                    reject_reason,
                    source_file,
                    rejected_at,
                    source_file_hash,
                    reference_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                source_row_number,
                row.get("event_id"),
                row.get("customer_id"),
                row.get("code"),
                row.get("event_date"),
                row.get("reject_reason"),
                source_file,
                rejected_at,
                source_file_hash,
                reference_version
            ))

            rejected_inserted += cursor.rowcount

        # 3. Record successful pipeline execution
        end_time = datetime.now(timezone.utc).isoformat()

        cursor.execute("""
            INSERT INTO pipeline_runs (
                run_id,
                source_file,
                reference_version,
                reference_file,
                start_time,
                end_time,
                status,
                input_count,
                accepted_count,
                rejected_count,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(run_id) DO UPDATE SET
                source_file = excluded.source_file,
                reference_version = excluded.reference_version,
                reference_file = excluded.reference_file,
                end_time = excluded.end_time,
                status = excluded.status,
                input_count = excluded.input_count,
                accepted_count = excluded.accepted_count,
                rejected_count = excluded.rejected_count,
                error_message = excluded.error_message
        """, (
            run_id,
            source_file,
            reference_version,
            reference_file,
            start_time,
            end_time,
            "SUCCESS",
            input_count,
            len(transformed_df),
            len(rejected_df),
            None
        ))

        connection.commit()

        return {
            "run_id": run_id,
            "accepted_inserted": accepted_inserted,
            "rejected_inserted": rejected_inserted,
            "accepted_count": len(transformed_df),
            "rejected_count": len(rejected_df),
            "status": "SUCCESS"
        }

    except Exception as error:

        connection.rollback()

        raise RuntimeError(
            f"Database loading failed: {error}"
        ) from error

    finally:
        connection.close()


if __name__ == "__main__":

    import uuid

    from src.extract import extract_data
    from src.validate import validate_data
    from src.transform import transform_data

    project_root = Path(__file__).resolve().parents[1]

    input_path = (
        project_root / "data" / "input" / "sample_incoming.csv"
    )

    reference_path = (
        project_root / "data" / "reference" / "reference_v2.csv"
    )

    db_path = (
        project_root / "data" / "output" / "reference_validation.db"
    )

    run_id = str(uuid.uuid4())

    start_time = datetime.now(timezone.utc).isoformat()

    source_df, reference_df = extract_data(
        input_path,
        reference_path
    )

    accepted_df, rejected_df = validate_data(
        source_df,
        reference_df
    )

    transformed_df = transform_data(
        accepted_df,
        reference_df,
        reference_version="v2"
    )

    result = load_data(
        transformed_df=transformed_df,
        rejected_df=rejected_df,
        db_path=db_path,
        run_id=run_id,
        source_file=input_path.name,
        input_count=len(source_df),
        started_at=start_time,
        reference_version="v2",
        reference_file=reference_path.name
    )

    print("\n========== LOAD REPORT ==========")
    print("Run ID:", result["run_id"])
    print("Input records:", len(source_df))
    print("Accepted inserted:", result["accepted_inserted"])
    print("Rejected inserted:", result["rejected_inserted"])
    print("Status:", result["status"])
