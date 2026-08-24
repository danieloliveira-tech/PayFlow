SELECT
    p.payment_method_type,
    COUNT(*) AS transaction_count,
    COUNT(*) FILTER (
        WHERE f.transaction_status = 'approved'
    ) AS approved_count,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE f.transaction_status = 'approved'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS approval_rate_pct
FROM gold.fact_transaction f
JOIN gold.dim_payment p
    ON p.payment_pk = f.payment_pk
GROUP BY p.payment_method_type
ORDER BY approval_rate_pct DESC;
