# AI Usage Documentation

## 1. Purpose

This document explains how AI tools supported the development of the Reference Data Validation Pipeline.

AI assistance was used for understanding technical concepts, exploring implementation approaches, debugging, designing tests, performance analysis, and improving documentation.

All final implementation decisions and project verification remain the developer's responsibility.

## 2. AI Tools Used

### ChatGPT

Used as the primary AI assistant for:
- Understanding the pipeline requirements.
- Python and Pandas implementation guidance.
- SQLite database and idempotency concepts.
- Debugging and test-case development.
- Performance optimization guidance.
- README and technical documentation improvements.

### Claude AI

Used occasionally as a secondary assistant for additional technical suggestions and alternative implementation approaches.

Specific Claude prompts and suggestions should be included in the separate prompt history where available.

## 3. Areas of AI Assistance

### 3.1 Architecture and Design
- Breaking the pipeline into extraction, validation, transformation, and loading stages.
- Understanding versioned reference data.
- Exploring database audit and run-tracking approaches.

### 3.2 Python Development
- Reviewing Pandas data validation approaches.
- Understanding SQLite transactions and database constraints.
- Exploring error handling and duplicate detection.

### 3.3 Testing
- Designing Pytest test cases.
- Testing missing fields, invalid dates, unknown codes, and duplicate records.
- Testing idempotency and retry behaviour.
- Adding an out-of-order event-date test.

### 3.4 Performance
- Exploring efficient Pandas iteration using `itertuples()`.
- Generating reproducible 100,000-record datasets.
- Reviewing extraction, validation, and transformation timings.

### 3.5 Documentation
- Improving README setup instructions.
- Preparing the data dictionary and design decisions.
- Documenting reference-version comparisons and SQL reconciliation.

## 4. Developer's Personal Review and Contributions

The developer reviewed the AI suggestions and performed implementation and verification activities.

Examples of work performed:

1. Added an automated test for out-of-order event dates and verified that all three records were processed independently.
2. Updated the synthetic data generator to use a fixed random seed and generate different data-quality scenarios.
3. Reviewed duplicate event ID handling and validation outcomes.
4. Executed the pipeline with reference versions v1 and v2 and checked accepted and rejected record counts.
5. Re-executed both v1 and v2 pipeline runs to verify that accepted and rejected records were not inserted again for the same source file and reference version.
6. Ran the automated test suite and verified that all 18 tests passed.
7. Checked the 100,000-record dataset generation and benchmark results.
8. Reviewed SQLite reconciliation results and GitHub synchronization.

The developer remains responsible for reviewing the implementation, understanding its limitations, and explaining the submitted code.

## 5. Limitations and Open Improvements

The project implements the core reference data validation workflow. However, some areas can be extended in future versions:

- The current implementation uses CSV files as the input data source.
- SQLite is used for local database storage; a production deployment could use a scalable database.
- Support for multiple validity periods for the same reference code can be extended.
- Distributed processing and large-scale orchestration are outside the current project scope.
- Additional monitoring and alerting capabilities can be introduced for production use.

These are potential future enhancements rather than failures of the implemented pipeline.

## 6. Prompt History

A separate file, `prompt_history.md`, is intended to contain the actual prompts submitted to ChatGPT and Claude AI.

This document is not a substitute for the complete prompt history. Any prompts that cannot be recovered must be identified honestly rather than reconstructed or presented as verbatim.

## 7. Confidentiality

Confidential assessment instructions, the original challenge statement, and restricted assessment material are not reproduced in this documentation.

## 8. Disclosure

AI tools were used as supporting development resources. The developer reviewed, tested, and adapted the suggestions used in the project and is responsible for the final submitted implementation.