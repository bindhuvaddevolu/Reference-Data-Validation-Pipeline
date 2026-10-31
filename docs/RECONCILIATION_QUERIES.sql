-- 1. Pipeline run-level reconciliation
-- Check whether input count = accepted count + rejected count.

SELECT
    run_id,
    source_file,
    reference_version,
    status,
    input_count,
    accepted_count,
    rejected_count,
    input_count - (accepted_count + rejected_count) AS reconciliation_difference
FROM pipeline_runs
ORDER BY start_time DESC;


-- 2. Actual accepted and rejected records attributed to each run.
-- Note: Accepted records inserted during an earlier run
-- retain that original run_id during idempotent reruns.

SELECT
    pr.run_id,
    pr.status,
    pr.input_count,
    pr.accepted_count AS processed_accepted_count,
    pr.rejected_count AS processed_rejected_count,
    (
        SELECT COUNT(*)
        FROM accepted_records ar
        WHERE ar.run_id = pr.run_id
    ) AS accepted_rows_attributed_to_run,
    (
        SELECT COUNT(*)
        FROM rejected_records rr
        WHERE rr.run_id = pr.run_id
    ) AS rejected_rows_attributed_to_run
FROM pipeline_runs pr
ORDER BY pr.start_time DESC;


-- 3. Rejected records grouped by rejection reason.

SELECT
    reject_reason,
    COUNT(*) AS rejected_count
FROM rejected_records
GROUP BY reject_reason
ORDER BY rejected_count DESC;


-- 4. Accepted records grouped by reference version.

SELECT
    reference_version,
    COUNT(*) AS accepted_count
FROM accepted_records
GROUP BY reference_version
ORDER BY reference_version;


-- 5. Check duplicate accepted records.
-- Expected result: No rows.

SELECT
    event_id,
    reference_version,
    COUNT(*) AS duplicate_count
FROM accepted_records
GROUP BY event_id, reference_version
HAVING COUNT(*) > 1;


-- 6. Inspect rejected records with source traceability.

SELECT
    run_id,
    source_file,
    source_row_number,
    event_id,
    customer_id,
    code,
    event_date,
    reject_reason
FROM rejected_records
ORDER BY rejected_at DESC;


-- 7. Check failed pipeline executions.

SELECT
    run_id,
    source_file,
    reference_version,
    status,
    error_message,
    start_time,
    end_time
FROM pipeline_runs
WHERE status = 'FAILED'
ORDER BY start_time DESC;