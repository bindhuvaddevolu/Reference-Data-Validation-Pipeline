# Project Results and Performance Report

## 1. Overview

This report summarizes the validation results, reference version comparison, and performance benchmark of the Reference Data Validation Pipeline.

## 2. Reference Version Comparison

The pipeline was executed using two reference dataset versions.

| Metric | Reference v1 | Reference v2 |
|---|---:|---:|
| Reference records | 5 | 6 |
| Input records | 12 | 12 |
| Accepted records | 3 | 4 |
| Rejected records | 9 | 8 |

### Key Observation

Reference v2 introduces the PNQ reference code.

The event associated with PNQ (E007) is accepted using reference v2 but is not accepted using reference v1.

This demonstrates how reference dataset updates can affect validation outcomes.

## 3. Performance Benchmark

The pipeline was benchmarked using 100,000 incoming records.

| Metric | Result |
|---|---:|
| Total input records | 100,000 |
| Accepted records | 57,238 |
| Rejected records | 42,762 |
| Extraction time | 0.3237 seconds |
| Validation time | 1.5814 seconds |
| Transformation time | 0.1158 seconds |
| Total processing time | 2.0208 seconds |
| Processing throughput | 49,484.20 records/second |

### Performance Observation

The validation stage took the largest share of the measured processing time.

The implementation uses efficient Pandas iteration with `itertuples()` to improve validation performance.

Note: The benchmark measures extraction, validation, and transformation. SQLite loading is not included in the reported processing time.

## 4. Automated Testing

The project includes 17 automated tests using Pytest.
Test coverage includes:

- Valid records
- Empty input
- Missing required fields
- Unknown reference codes
- Expired reference codes
- Future effective dates
- Historical deprecated codes
- Invalid event dates
- Duplicate event IDs
- Duplicate reference codes
- Database idempotency
- Source row number traceability
- Retry behavior
- Reference version audit metadata
- Missing source column detection
- Unexpected source column detection
- Malformed CSV detection

### Test Result

17 tests passed successfully.

## 5. Database and Reliability

The SQLite database maintains:

- Accepted records
- Rejected records
- Pipeline execution history

The pipeline uses idempotent loading for accepted records and maintains rejection history by pipeline run.

Source row numbers and reference version metadata support traceability and auditability.

## 6. Conclusion

The project successfully demonstrates a modular reference data validation pipeline with version-aware validation, data transformation, SQLite persistence, automated tests, retry handling, audit logging, and large-file performance benchmarking.
## SQL Reconciliation and Database Verification

The SQLite database was verified using the SQL queries available in `docs/RECONCILIATION_QUERIES.sql`.

### Reconciliation Results

| Reference Version | Input Records | Accepted Records | Rejected Records | Difference |
|---|---:|---:|---:|---:|
| v1 | 12 | 3 | 9 | 0 |
| v2 | 12 | 4 | 8 | 0 |

### Database Validation

- Input, accepted, and rejected counts reconciled successfully.
- No duplicate accepted records were found for the composite key `(event_id, reference_version)`.
- Accepted records were verified separately for reference versions v1 and v2.
- Rejected records retained their rejection reasons and source row numbers.
- Failed pipeline execution details were available in the `pipeline_runs` table.
- Repeated executions demonstrated idempotent accepted-record loading.

### Observation

Accepted records retain the run ID of the execution that first inserted them. During subsequent idempotent executions, existing accepted records are not inserted again. Pipeline execution counts are maintained separately in `pipeline_runs`.

Rejection audit records are maintained per run, so rejection counts across multiple executions may accumulate.