SELECT
    m.merchant_category,
    COUNT(*) AS transaction_count,
    ROUND(SUM(f.amount), 2) AS total_amount,
    ROUND(AVG(f.amount), 2) AS average_ticket
FROM gold.fact_transaction f
JOIN gold.dim_merchant m
    ON m.merchant_pk = f.merchant_pk
GROUP BY m.merchant_category
ORDER BY total_amount DESC;
