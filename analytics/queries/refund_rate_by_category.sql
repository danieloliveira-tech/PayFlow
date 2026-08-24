SELECT
    m.merchant_category,
    COUNT(*) AS transaction_count,
    COUNT(*) FILTER (
        WHERE f.transaction_status = 'refunded'
    ) AS refunded_count,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE f.transaction_status = 'refunded'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS refund_rate_pct
FROM gold.fact_transaction f
JOIN gold.dim_merchant m
    ON m.merchant_pk = f.merchant_pk
GROUP BY m.merchant_category
ORDER BY refund_rate_pct DESC;
