# Data Dictionary
## Reference Data Validation Pipeline

### 1. Project Overview

This document describes the source data, reference data, target database tables, column definitions, keys, and business rules used in the Reference Data Validation Pipeline.

### 2. Source Dataset – Incoming Records

File: `sample_incoming.csv`

Location: `data/input/`

| Column | Data Type | Required | Description |
|---|---|---|---|
| event_id | String | Yes | Unique identifier for an event |
| customer_id | String | Yes | Identifier of the customer |
| code | String | Yes | Code to validate against reference data |
| event_date | Date (ISO-8601) | Yes | Date associated with the event |

**Key:** `event_id` is expected to be unique.

### 3. Reference Datasets

Files:
- `reference_v1.csv`
- `reference_v2.csv`

Location: `data/reference/`

| Field | Data Type | Description |
|---|---|---|
| code | String | Reference code |
| description | String | Description of the code |
| status | String | ACTIVE or DEPRECATED |
| valid_from | Date | Start of validity period |
| valid_to | Date / Nullable | End of validity period |

Reference codes are used to validate incoming records. Reference versions allow the pipeline to process data against different versions of reference information.

### 4. Target Database Tables

Database: `reference_validation.db`

#### 4.1 accepted_records

Stores successfully validated and transformed records.

| Column | Description |
|---|---|
| event_id | Event identifier |
| customer_id | Customer identifier |
| code | Validated reference code |
| description | Reference description |
| event_date | Event date |
| reference_status | Reference status |
| reference_version | Reference dataset version |
| event_year | Year derived from event_date |
| event_month | Month derived from event_date |
| validation_warning | Warning for applicable records |
| source_file | Original input filename |
| source_row_number | Original CSV row number |
| run_id | Pipeline execution identifier |
| loaded_at | Database load timestamp |

**Primary key:** `(event_id, reference_version)`

#### 4.2 rejected_records

Stores records that fail validation.

| Column | Description |
|---|---|
| run_id | Pipeline execution identifier |
| source_row_number | Original CSV row number |
| event_id | Event identifier, if available |
| customer_id | Customer identifier, if available |
| code | Incoming reference code |
| event_date | Incoming event date |
| reject_reason | Reason for rejection |
| source_file | Original input filename |
| rejected_at | Rejection timestamp |

**Primary key:** `(run_id, source_row_number)`

#### 4.3 pipeline_runs

Stores pipeline execution and audit information.

| Column | Description |
|---|---|
| run_id | Unique pipeline execution identifier |
| source_file | Input filename |
| reference_version | Reference dataset version |
| reference_file | Reference filename |
| start_time | Pipeline start timestamp |
| end_time | Pipeline completion timestamp |
| status | SUCCESS or FAILED |
| input_count | Total input records |
| accepted_count | Accepted record count |
| rejected_count | Rejected record count |
| error_message | Failure details, if applicable |

**Primary key:** `run_id`

### 5. Business Rules

1. Required incoming fields must not be missing.
2. Duplicate event IDs are rejected.
3. Unknown reference codes are rejected.
4. Event dates before `valid_from` are rejected as `NOT_YET_VALID`.
5. Event dates after `valid_to` are rejected as `EXPIRED_CODE`.
6. Historical records for deprecated codes within their validity period are accepted with a warning.
7. Reference status must be ACTIVE or DEPRECATED.
8. The `valid_to` date is inclusive.
9. Original source row numbers are preserved for traceability.

### 6. Data Quality and Reconciliation

The pipeline separates records into accepted and rejected datasets.

The following reconciliation rule is applied:

`Input Count = Accepted Count + Rejected Count`

Rejected records retain their source file, source row number, and rejection reason for traceability.

### 7. Assumptions

- Incoming and reference datasets are provided as CSV files.
- Sample datasets are synthetic and created for reproducible testing.
- Dates are interpreted using ISO-8601 format.
- Reference versions are selected through a pipeline parameter.
- SQLite is used as the local target database.
- The original input records are not silently overwritten during validation.