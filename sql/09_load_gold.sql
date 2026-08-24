BEGIN;

CREATE TEMP TABLE current_gold_batch ON COMMIT DROP AS

SELECT
    t.transaction_id,
    t.transaction_at,
    t.transaction_amount,
    t.transaction_status,

    c.customer_id,
    c.customer_status,
    c.customer_city,
    c.customer_state,
    c.customer_region,

    m.merchant_id,
    m.merchant_name,
    m.merchant_category,
    m.merchant_status,
    m.merchant_city,
    m.merchant_state,
    m.merchant_region,

    p.payment_method_id,
    p.payment_method_name,
    p.payment_method_type,
    p.payment_method_brand

FROM silver.transactions t

JOIN silver.customers c ON c.customer_id = t.customer_id

JOIN silver.merchants m ON m.merchant_id = t.merchant_id

JOIN silver.payment_methods p ON p.payment_method_id = t.payment_method_id

WHERE NOT EXISTS (
    SELECT 1
    FROM gold.fact_transaction f
    WHERE f.transaction_pk = t.transaction_id
);


--inserir na dimensão tempo
INSERT INTO gold.dim_datetime (
    full_datetime,
    hour,
    day,
    month,
    year,
    day_of_the_week,
    quarter,
    semester
)
SELECT DISTINCT
    date_trunc(
        'hour',
        transaction_at AT TIME ZONE 'America/Sao_Paulo'
    ) AS full_datetime,

    EXTRACT(
        HOUR FROM transaction_at AT TIME ZONE 'America/Sao_Paulo'
    )::SMALLINT,

    EXTRACT(
        DAY FROM transaction_at AT TIME ZONE 'America/Sao_Paulo'
    )::SMALLINT,

    EXTRACT(
        MONTH FROM transaction_at AT TIME ZONE 'America/Sao_Paulo'
    )::SMALLINT,

    EXTRACT(
        YEAR FROM transaction_at AT TIME ZONE 'America/Sao_Paulo'
    )::SMALLINT,

    EXTRACT(
        ISODOW FROM transaction_at AT TIME ZONE 'America/Sao_Paulo'
    )::SMALLINT,

    EXTRACT(
        QUARTER FROM transaction_at AT TIME ZONE 'America/Sao_Paulo'
    )::SMALLINT,

    CASE
        WHEN EXTRACT(
            MONTH FROM transaction_at AT TIME ZONE 'America/Sao_Paulo'
        ) <= 6
            THEN 1
        ELSE 2
    END::SMALLINT

FROM current_gold_batch

ON CONFLICT (full_datetime) DO NOTHING;

--inserir na dimensão de pagamento
INSERT INTO gold.dim_payment (
    payment_method_id,
    payment_method_name,
    payment_method_type,
    payment_method_brand
)
SELECT DISTINCT
    payment_method_id,
    payment_method_name,
    payment_method_type,
    payment_method_brand
FROM current_gold_batch

ON CONFLICT (payment_method_id) DO NOTHING;

--inserir na dimensão de comerciante
INSERT INTO gold.dim_merchant (
    merchant_id,
    merchant_name,
    merchant_category,
    merchant_status
)
SELECT DISTINCT
    merchant_id,
    merchant_name,
    merchant_category,
    merchant_status
FROM current_gold_batch

ON CONFLICT (merchant_id) DO NOTHING;


--inserir na dimensão de localização
INSERT INTO gold.dim_location (
    city,
    state,
    region
)

SELECT DISTINCT
    customer_city,
    customer_state,
    customer_region
FROM current_gold_batch

UNION

SELECT DISTINCT
    merchant_city,
    merchant_state,
    merchant_region
FROM current_gold_batch

ON CONFLICT (city, state, region) DO NOTHING;

--inserir na fato
INSERT INTO gold.fact_transaction (
    transaction_pk,
    datetime_pk,
    payment_pk,
    merchant_pk,
    merchant_location_pk,
    customer_location_pk,
    customer_id,
    transaction_status,
    customer_status,
    amount
)

SELECT
    b.transaction_id,
    dt.datetime_pk,
    p.payment_pk,
    m.merchant_pk,
    merchant_location.location_pk,
    customer_location.location_pk,
    b.customer_id,
    b.transaction_status,
    b.customer_status,
    b.transaction_amount

FROM current_gold_batch b

JOIN gold.dim_datetime dt ON dt.full_datetime = date_trunc('hour', b.transaction_at AT TIME ZONE 'America/Sao_Paulo')
JOIN gold.dim_payment p ON p.payment_method_id = b.payment_method_id
JOIN gold.dim_merchant m ON m.merchant_id = b.merchant_id
JOIN gold.dim_location merchant_location ON merchant_location.city = b.merchant_city AND merchant_location.state = b.merchant_state AND merchant_location.region = b.merchant_region
JOIN gold.dim_location customer_location ON customer_location.city = b.customer_city AND customer_location.state = b.customer_state AND customer_location.region = b.customer_region

ON CONFLICT (transaction_pk) DO NOTHING;


COMMIT;