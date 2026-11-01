# Project Results and Performance Report

## 1. Overview

This report summarizes the validation results, reference version comparison, performance benchmark, automated testing, and database reconciliation of the Reference Data Validation Pipeline.

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

This demonstrates how reference dataset updates can affect validation outcomes without modifying the incoming source data.

## 3. Performance Benchmark

The pipeline was benchmarked using a reproducible synthetic dataset containing 100,000 incoming records.

### Dataset Distribution

| Scenario | Generated Records |
|---|---:|
| Normal records | 92,000 |
| Duplicate records | 2,000 |
| Missing required fields | 2,000 |
| Invalid dates | 2,000 |
| Unknown reference codes | 2,000 |
| **Total** | **100,000** |

### Benchmark Results

| Metric | Result |
|---|---:|
| Total input records | 100,000 |
| Accepted records | 60,226 |
| Rejected records | 39,774 |
| Extraction time | 0.3270 seconds |
| Validation time | 1.4083 seconds |
| Transformation time | 0.1100 seconds |
| Total processing time | 1.8453 seconds |
| Processing throughput | 54,192.22 records/second |

### Performance Observation

The validation stage took the largest share of the measured processing time.

The implementation uses Pandas iteration with `itertuples()` to process incoming records efficiently.

The benchmark measures extraction, validation, and transformation. SQLite loading time is not included in the reported processing time.

The dataset generator uses a fixed random seed (42) and supports configurable record counts through the `--size` argument.

Benchmark timings may vary depending on hardware and system conditions.

## 4. Automated Testing

The project includes **18 automated tests** using Pytest.

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
- Out-of-order event dates

### Test Result

**18 tests passed successfully.**

Command used:

```bash
python -m pytest tests/ -v
```

## 5. Database and Reliability

The SQLite database maintains three main tables:

- `accepted_records` – stores validated and transformed records.
- `rejected_records` – stores rejected records with rejection reasons and source traceability.
- `pipeline_runs` – maintains pipeline execution history, status, and record counts.

### Accepted Record Idempotency

The pipeline uses a composite primary key `(event_id, reference_version)` for accepted records.

This prevents duplicate accepted records when the same event is processed repeatedly using the same reference version.

### Rejected Record Idempotency

Rejected records are deduplicated using a combination of:

- Source file SHA-256 hash.
- Source row number.
- Reference version.

This prevents duplicate rejected-record entries when the same source file is processed again using the same reference version.

### Execution Auditing

Every pipeline execution receives a unique run ID and is recorded separately in the `pipeline_runs` table, including repeated executions.

Accepted and rejected records retain the run ID of the execution that first inserted them.

This approach maintains record-level traceability while keeping individual pipeline execution history available for auditing.

Source file details, source row numbers, rejection reasons, run IDs, and reference version metadata support troubleshooting and traceability.

## 6. SQL Reconciliation and Database Verification

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
- Rejected-record idempotency was verified using source file hash, source row number, and reference version.
- Pipeline execution details were recorded separately in the `pipeline_runs` table.
- Repeated executions did not create unintended duplicate accepted or rejected records.

### Observation

The pipeline successfully processed both reference versions and maintained consistent validation results across repeated executions.

The reconciliation results confirm that the number of input records matches the combined accepted and rejected records for each reference version.

## 7. Conclusion

The Reference Data Validation Pipeline successfully demonstrates a modular data engineering workflow covering data extraction, schema validation, business rule validation, transformation, and database loading.

The implementation supports versioned reference data, record-level traceability, audit logging, automated testing, reproducible data generation, and idempotent processing.

The successful v1 and v2 executions, repeated-run verification, and automated test results demonstrate the reliability and reproducibility of the implemented solution.