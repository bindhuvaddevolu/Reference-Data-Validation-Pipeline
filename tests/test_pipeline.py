
import sqlite3

import pandas as pd
import pytest

from src.validate import validate_data
from src.transform import transform_data
from src.load import load_data


@pytest.fixture
def reference_df():
    """Sample reference dataset for testing."""

    return pd.DataFrame([
        {
            "code": "HYD",
            "description": "Hyderabad",
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
    ])


def make_source(records):
    """Create incoming records for tests."""

    return pd.DataFrame(
        records,
        columns=[
            "event_id",
            "customer_id",
            "code",
            "event_date",
        ],
    )


# TEST 1: Valid record should be accepted
def test_valid_record(reference_df):

    source_df = make_source([
        ["E001", "C001", "HYD", "2026-10-20"]
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    assert len(accepted) == 1
    assert len(rejected) == 0


# TEST 2: Empty input should not fail
def test_empty_input(reference_df):

    source_df = make_source([])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    assert len(accepted) == 0
    assert len(rejected) == 0


# TEST 3: Missing customer ID
def test_missing_customer_id(reference_df):

    source_df = make_source([
        ["E002", "", "HYD", "2026-10-20"]
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    assert len(accepted) == 0
    assert "MISSING_CUSTOMER_ID" in rejected.iloc[0]["reject_reason"]


# TEST 4: Unknown reference code
def test_unknown_code(reference_df):

    source_df = make_source([
        ["E003", "C003", "XYZ", "2026-10-20"]
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    assert len(accepted) == 0
    assert "UNKNOWN_CODE" in rejected.iloc[0]["reject_reason"]


# TEST 5: Expired reference code
def test_expired_code(reference_df):

    source_df = make_source([
        ["E004", "C004", "OLD", "2026-06-15"]
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    assert len(accepted) == 0
    assert "EXPIRED_CODE" in rejected.iloc[0]["reject_reason"]


# TEST 6: Future effective code
def test_future_effective_code(reference_df):

    source_df = make_source([
        ["E005", "C005", "FUT", "2026-10-20"]
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    assert len(accepted) == 0
    assert "NOT_YET_VALID" in rejected.iloc[0]["reject_reason"]


# TEST 7: Historical deprecated code
def test_historical_deprecated_code(reference_df):

    source_df = make_source([
        ["E006", "C006", "OLD", "2024-06-15"]
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    assert len(accepted) == 1
    assert len(rejected) == 0

    assert (
        accepted.iloc[0]["validation_warning"]
        == "HISTORICAL_DEPRECATED_CODE"
    )


# TEST 8: Invalid event date
def test_invalid_event_date(reference_df):

    source_df = make_source([
        ["E007", "C007", "HYD", "not-a-date"]
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    assert len(accepted) == 0
    assert "INVALID_EVENT_DATE" in rejected.iloc[0]["reject_reason"]


# TEST 9: Both duplicate event IDs should be rejected
def test_duplicate_event_ids(reference_df):

    source_df = make_source([
        ["E008", "C008", "HYD", "2026-10-20"],
        ["E008", "C009", "HYD", "2026-10-21"],
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    assert len(accepted) == 0
    assert len(rejected) == 2

    assert all(
        rejected["reject_reason"].str.contains("DUPLICATE_EVENT_ID")
    )


# TEST 10: Duplicate reference codes should fail
def test_duplicate_reference_codes(reference_df):

    duplicate = reference_df.iloc[[0]].copy()

    invalid_reference = pd.concat(
        [reference_df, duplicate],
        ignore_index=True
    )

    source_df = make_source([
        ["E009", "C009", "HYD", "2026-10-20"]
    ])

    with pytest.raises(ValueError, match="Duplicate reference code"):
        validate_data(source_df, invalid_reference)


# TEST 11: Database load should be idempotent
def test_database_idempotency(reference_df, tmp_path):

    source_df = make_source([
        ["E010", "C010", "HYD", "2026-10-20"]
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    transformed = transform_data(
        accepted,
        reference_df,
        reference_version="v1"
    )

    database_path = tmp_path / "test.db"

    run_id = "test-run-001"

    first_result = load_data(
        transformed,
        rejected,
        database_path,
        run_id,
        "test.csv",
        len(source_df),
        reference_version="v1",
        reference_file="reference_v1.csv"
    )

    second_result = load_data(
        transformed,
        rejected,
        database_path,
        run_id,
        "test.csv",
        len(source_df),
        reference_version="v1",
        reference_file="reference_v1.csv"
    )

    assert first_result["accepted_inserted"] == 1
    assert second_result["accepted_inserted"] == 0


# TEST 12: Original source row numbers should be preserved
def test_source_row_numbers(reference_df):

    source_df = make_source([
        ["E011", "C011", "HYD", "2026-10-20"],
        ["E012", "C012", "XYZ", "2026-10-21"],
        ["E013", "C013", "HYD", "2026-10-22"],
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    assert accepted["source_row_number"].tolist() == [1, 3]
    assert rejected["source_row_number"].tolist() == [2]


# TEST 13: Retry with a new run ID should preserve rejection history
def test_retry_with_new_run_id(reference_df, tmp_path):

    source_df = make_source([
        ["E014", "C014", "HYD", "2026-10-20"],
        ["E015", "C015", "XYZ", "2026-10-21"],
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    transformed = transform_data(
        accepted,
        reference_df,
        reference_version="v2"
    )

    database_path = tmp_path / "retry_test.db"

    # First pipeline execution
    first_result = load_data(
        transformed,
        rejected,
        database_path,
        "run-001",
        "test.csv",
        len(source_df),
        reference_version="v2",
        reference_file="reference_v2.csv"
    )

    # Second execution with a different run ID
    second_result = load_data(
        transformed,
        rejected,
        database_path,
        "run-002",
        "test.csv",
        len(source_df),
        reference_version="v2",
        reference_file="reference_v2.csv"
    )

    # Accepted record should not be duplicated
    assert first_result["accepted_inserted"] == 1
    assert second_result["accepted_inserted"] == 0

    # Rejected record should be audited for each run
    assert first_result["rejected_inserted"] == 1
    assert second_result["rejected_inserted"] == 1

    connection = sqlite3.connect(database_path)

    accepted_count = connection.execute(
        "SELECT COUNT(*) FROM accepted_records"
    ).fetchone()[0]

    rejected_count = connection.execute(
        "SELECT COUNT(*) FROM rejected_records"
    ).fetchone()[0]

    connection.close()

    assert accepted_count == 1
    assert rejected_count == 2


# TEST 14: Reference version should be stored in audit table
def test_reference_version_audit(reference_df, tmp_path):

    source_df = make_source([
        ["E016", "C016", "HYD", "2026-10-20"]
    ])

    accepted, rejected = validate_data(
        source_df,
        reference_df
    )

    transformed = transform_data(
        accepted,
        reference_df,
        reference_version="v2"
    )

    database_path = tmp_path / "audit_test.db"

    load_data(
        transformed,
        rejected,
        database_path,
        "audit-run-001",
        "test.csv",
        len(source_df),
        reference_version="v2",
        reference_file="reference_v2.csv"
    )

    connection = sqlite3.connect(database_path)

    audit_record = connection.execute("""
        SELECT
            source_file,
            reference_version,
            reference_file,
            status,
            input_count,
            accepted_count,
            rejected_count
        FROM pipeline_runs
        WHERE run_id = ?
    """, ("audit-run-001",)).fetchone()

    connection.close()

    assert audit_record == (
        "test.csv",
        "v2",
        "reference_v2.csv",
        "SUCCESS",
        1,
        1,
        0
    )
