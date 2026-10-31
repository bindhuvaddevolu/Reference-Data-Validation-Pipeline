
## Project: Reference Data Validation Pipeline

### 1. Project Architecture
Act as a senior data engineer. Analyze the Reference Data Validation Pipeline requirements and design a modular, scalable, and maintainable Python project architecture. Explain the responsibilities of each module and the data flow from ingestion to publishing.

### 2. Data Modeling and Schema Design
Design appropriate source and target schemas for the pipeline. Define primary keys, foreign keys, data types, nullability, relationships, record grain, and business assumptions. Use consistent snake_case naming conventions.

### 3. Synthetic Data Generation
Develop a reproducible Python data generator that creates realistic sample datasets of different sizes. Include valid records and controlled data-quality issues such as missing values, duplicate IDs, invalid dates, unknown reference codes, and expired reference records. Use a fixed random seed.

### 4. Data Ingestion
Implement a robust CSV ingestion module using Pandas. Handle empty files, missing columns, unexpected columns, malformed records, and incorrect data types. Preserve source row numbers for traceability.

### 5. Data Quality Validation
Implement a reusable validation framework that checks required fields, uniqueness, referential integrity, date validity, and reference-data effective periods. Separate accepted and rejected records and provide clear rejection reasons.

### 6. Reference Data Versioning
Support multiple reference data versions, including v1 and v2. Explain how historical reference changes should be handled and ensure that records are validated against the selected reference version.

### 7. Data Transformation
Create a transformation module that enriches accepted source records with reference descriptions, status, reference version, and derived date attributes. Ensure transformations are deterministic and consistent.

### 8. Database Design and Loading
Design a SQLite database schema to store accepted records, rejected records, and pipeline execution metadata. Implement transactional loading, primary-key constraints, and appropriate indexes.

### 9. Idempotency and Recovery
Implement idempotent pipeline execution. Reprocessing the same source file must not create unintended duplicate records. Design a reliable strategy for tracking processed files, handling rejected records, and recovering from partial failures.

### 10. Pipeline Observability
Implement pipeline execution logging with run IDs, source file details, start and end timestamps, execution status, input counts, accepted counts, rejected counts, and error details. Ensure that record counts can be reconciled.

### 11. Automated Testing
Create comprehensive Pytest test cases covering successful processing, missing values, duplicate records, invalid dates, unknown reference codes, empty input, schema changes, repeated execution, partial failures, and recovery scenarios.

### 12. Performance Optimization
Analyze the performance of the pipeline with 10,000, 50,000, and 100,000 records. Identify bottlenecks and optimize Pandas operations and database loading. Measure execution time and throughput before and after optimization.

### 13. Reconciliation and SQL Verification
Write SQL queries to verify input, accepted, and rejected record counts. Check primary-key uniqueness, referential integrity, duplicate records, and consistency between pipeline execution logs and database records.

### 14. Documentation
Prepare professional project documentation covering setup instructions, architecture, data dictionary, validation rules, design decisions, execution commands, testing instructions, performance results, and known limitations.

### 15. Final Code Review
Act as a senior data engineering reviewer. Evaluate the complete implementation against the project requirements. Identify functional gaps, edge cases, performance issues, security concerns, and improvements required before submission.

### 16. Reproducibility Review
Verify that a new developer can clone the repository, install dependencies, generate sample data, execute the pipeline, run tests, and reproduce the documented results using the README instructions.