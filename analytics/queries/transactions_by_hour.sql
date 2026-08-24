SELECT
    dt.hour,
    COUNT(*) AS transaction_count,
    ROUND(SUM(f.amount), 2) AS total_amount
FROM gold.fact_transaction f
JOIN gold.dim_datetime dt
    ON dt.datetime_pk = f.datetime_pk
GROUP BY dt.hour
ORDER BY dt.hour;
