# Design Decisions and Trade-offs

## 1. Overview

This document explains the key technical decisions made while developing the Reference Data Validation Pipeline and the trade-offs considered.

## 2. Technology Choices

| Technology | Reason for Selection | Trade-off |
|---|---|---|
| Python | Simple, readable, and suitable for data processing. | Performance may be lower than compiled languages for very large workloads. |
| Pandas | Provides convenient CSV processing and data manipulation. | Memory usage can increase with large datasets. |
| SQLite | Lightweight relational database that runs locally without a separate database server. | Less suitable for highly concurrent, large-scale production workloads. |
| CSV | Simple and portable format for source and reference datasets. | Limited support for complex data types and schema enforcement. |
| Pytest | Supports automated and repeatable testing. | Requires additional test maintenance as features grow. |

## 3. Reference Data Versioning

**Decision:** Maintain separate reference datasets such as `reference_v1.csv` and `reference_v2.csv`.

**Reason:** This allows the pipeline to validate the same incoming records against different reference versions and compare the results.

**Trade-off:** Multiple reference files require version management and audit tracking.

## 4. Data Validation Strategy

**Decision:** Separate validation logic from extraction and transformation.

**Reason:** Modular validation makes business rules easier to understand, test, maintain, and extend.

**Trade-off:** More modules introduce additional code organization and integration requirements.

## 5. Accepted and Rejected Records

**Decision:** Store accepted and rejected records separately.

**Reason:** Accepted records are ready for downstream consumption, while rejected records retain their rejection reasons for troubleshooting and correction.

**Trade-off:** Maintaining separate datasets requires additional storage and audit management.

## 6. Idempotent Loading

**Decision:** Use a composite primary key `(event_id, reference_version)` for accepted records and `INSERT OR IGNORE` during loading.

For rejected records, use a unique combination of `source_file_hash`, `source_row_number`, and `reference_version` to prevent duplicate rejection entries during repeated processing.

**Reason:** Reprocessing the same source file against the same reference version should not create unintended duplicate accepted or rejected records.

The source file hash helps identify the input file, while the source row number identifies the specific rejected record.

Every pipeline execution is recorded separately in the `pipeline_runs` table, including repeated executions. A rejected record retains the run ID of the execution that first inserted it.

**Trade-off:** Rejected records are deduplicated across repeated executions for the same source file and reference version. Therefore, individual reruns are tracked in `pipeline_runs` rather than creating duplicate rejected-record entries.

## 7. Audit and Traceability

**Decision:** Maintain a `pipeline_runs` table and preserve source row numbers.

**Reason:** Pipeline operators can identify execution status, processing counts, failure information, and the original source location of a record.

**Trade-off:** Audit tables increase database storage and require maintenance.

## 8. Performance Considerations

**Decision:** Use Pandas-based processing and benchmark a 100,000-record dataset.

**Reason:** Performance measurements help evaluate processing speed and identify optimization opportunities.

**Trade-off:** The current benchmark measures extraction, validation, and transformation, but excludes SQLite loading.

## 9. Limitations and Future Improvements

- Replace SQLite with a production database for larger concurrent workloads.
- Introduce incremental processing for continuously arriving data.
- Add cloud storage and orchestration.
- Include database loading in performance benchmarks.
- Add monitoring dashboards and automated alerts.
- Explore distributed processing for significantly larger datasets.

## 10. Conclusion

The solution prioritizes correctness, reproducibility, traceability, modularity, and ease of local execution. The selected technologies provide a lightweight and understandable implementation suitable for demonstrating reference-data validation concepts.