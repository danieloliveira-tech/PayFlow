SELECT
    customer_location.region AS customer_region,
    merchant_location.region AS merchant_region,
    COUNT(*) AS transaction_count,
    ROUND(SUM(f.amount), 2) AS total_amount
FROM gold.fact_transaction f
JOIN gold.dim_location customer_location
    ON customer_location.location_pk = f.customer_location_pk
JOIN gold.dim_location merchant_location
    ON merchant_location.location_pk = f.merchant_location_pk
GROUP BY
    customer_location.region,
    merchant_location.region
ORDER BY transaction_count DESC;
