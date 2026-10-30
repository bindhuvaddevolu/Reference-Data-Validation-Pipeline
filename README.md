# Reference Data Validation Pipeline

## Project Overview

The Reference Data Validation Pipeline is a Python-based data engineering project designed to validate incoming data against versioned reference datasets, transform valid records, and load accepted and rejected records into a SQLite database.

The pipeline supports reference data versioning, data quality checks, duplicate detection, audit logging, retry handling, and performance benchmarking.

## Key Features

- CSV data extraction using Pandas.
- Reference data validation with effective date checks.
- Detection of missing fields and unknown reference codes.
- Duplicate event ID detection.
- Historical deprecated code validation with warnings.
- Data transformation and enrichment.
- SQLite database integration.
- Idempotent data loading to prevent duplicate accepted records.
- Retry handling and failure auditing.
- Source row-level traceability.
- Reference version tracking.
- Automated testing using Pytest.
- Performance benchmarking for large datasets.

## Project Architecture

```text
Reference-Data-Validation-Pipeline/
│
├── data/
│   ├── input/
│   ├── reference/
│   └── output/
│
├── src/
│   ├── generator.py
│   ├── extract.py
│   ├── validate.py
│   ├── transform.py
│   ├── load.py
│   ├── pipeline.py
│   ├── benchmark.py
│   └── compare_reference_versions.py
│
├── tests/
│   └── test_pipeline.py
│
├── prompts/
├── reports/
├── logs/
│
├── requirements.txt
└── README.md
```

## Technologies Used

- Python
- Pandas
- SQLite
- Pytest
- CSV
- Git and GitHub

## Data Validation Rules

The pipeline applies the following validation rules:

1. Required fields must not be empty.
2. Event IDs must be unique.
3. Unknown reference codes are rejected.
4. Events before the reference effective date are rejected.
5. Expired reference codes are rejected.
6. Historical events using deprecated codes are accepted with a warning when they fall within the valid period.
7. Invalid event dates are rejected.
8. Duplicate reference codes cause reference validation to fail.

## Reference Version Comparison

The project supports two reference datasets:

| Metric | Reference v1 | Reference v2 |
|---|---:|---:|
| Reference records | 5 | 6 |
| Input records | 12 | 12 |
| Accepted records | 3 | 4 |
| Rejected records | 9 | 8 |

Reference v2 introduces the PNQ code, resulting in one additional accepted record compared with v1.

## Installation

Clone the repository:

```bash
git clone https://github.com/bindhuvaddevolu/Reference-Data-Validation-Pipeline.git
cd Reference-Data-Validation-Pipeline
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Pipeline

Run using reference version v1:

```bash
python -m src.pipeline --reference-version v1
```

Run using reference version v2:

```bash
python -m src.pipeline --reference-version v2
```

## Run Automated Tests

```bash
python -m pytest tests/ -v
```

The project currently includes 14 automated tests covering validation, duplicate detection, source traceability, idempotency, retry behavior, and audit metadata.

## Performance Benchmark

Run the benchmark:

```bash
python -m src.benchmark
```

Latest benchmark results:

| Metric | Result |
|---|---:|
| Input records | 100,000 |
| Accepted records | 57,238 |
| Rejected records | 42,762 |
| Total processing time | 2.0208 seconds |
| Throughput | 49,484 records/second |

Note: Benchmark timing covers extraction, validation, and transformation; it does not include SQLite loading.

## Database and Audit

SQLite stores:

- Accepted records
- Rejected records
- Pipeline execution history

Each pipeline execution records its run ID, source file, reference version, reference filename, execution status, record counts, and timestamps.

Source row numbers are preserved to support record-level traceability.

## Future Improvements

- Add automated scheduling.
- Add data quality dashboards.
- Support additional input formats.
- Add structured monitoring and alerting.
- Extend performance testing to database loading.

## Author

Developed as an individual data engineering project.
