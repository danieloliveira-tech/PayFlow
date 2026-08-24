WITH
clean AS (
	SELECT	transaction_id,
			transaction_at,
			transaction_amount,
			LOWER(TRIM(transaction_status))		AS transaction_status,
			
			customer_id,
			INITCAP(TRIM(customer_name))			AS customer_name,
			LOWER(TRIM(customer_email)) 			AS customer_email,
			INITCAP(TRIM(customer_city)) 			AS customer_city,
			UPPER(TRIM(customer_state)) 			AS customer_state,
			LOWER(TRIM(customer_status)) 			AS customer_status,
			
			merchant_id,
			INITCAP(TRIM(merchant_name)) 			AS merchant_name,
			LOWER(TRIM(merchant_category)) 		AS merchant_category,
			INITCAP(TRIM(merchant_city)) 			AS merchant_city,
			UPPER(TRIM(merchant_state)) 			AS merchant_state,
			LOWER(TRIM(merchant_status)) 			AS merchant_status,
			
			payment_method_id,
			INITCAP(TRIM(payment_method_name)) 	AS payment_method_name,
			LOWER(TRIM(payment_method_type)) 		AS payment_method_type,
			INITCAP(TRIM(payment_method_brand))	AS payment_method_brand,
			
			source_file,
			ingested_at
		FROM bronze.transactions_raw
),

clean_classified AS (
	SELECT *,		
		CASE
			WHEN transaction_amount <= 0 THEN 'INVALID_AMOUNT'
			WHEN transaction_id IS NULL THEN 'NULL_TRANSACTION_ID'
			WHEN customer_id IS NULL THEN 'NULL_CUSTOMER_ID'
			WHEN transaction_status = 'unknown' THEN 'TRANSACTION_STATUS_INVALID'
			ELSE NULL
		END AS rejection_reason
	FROM clean	
),

insert_rejected AS (
	INSERT INTO silver.rejected_transactions (
		transaction_id, 
		ingested_at, 
		source_file, 
		rejection_reason
	)
	SELECT
		transaction_id,
		ingested_at,
		source_file,
		rejection_reason
	FROM clean_classified
	WHERE rejection_reason IS NOT NULL
	RETURNING 1
),

insert_payment_method AS (
	INSERT INTO silver.payment_methods (
		payment_method_id,
		payment_method_name,
		payment_method_type,
		payment_method_brand
	)
	SELECT
		payment_method_id,
		payment_method_name,
		payment_method_type,
		payment_method_brand
	FROM (
		SELECT
			payment_method_id,
			payment_method_name,
			payment_method_type,
			payment_method_brand,
			ROW_NUMBER() OVER (
				PARTITION BY payment_method_id
				ORDER BY ingested_at, transaction_id
			) AS rn
		FROM clean_classified
		WHERE payment_method_type IN ('pix', 'credit_card', 'debit_card')
	) sub
	WHERE sub.rn = 1
	RETURNING payment_method_id
),

insert_customer AS (
	INSERT INTO silver.customers (
		customer_id,
		customer_name,
		customer_email,
		customer_city,
		customer_state,
		customer_region,
		customer_status,
		first_seen_at
	)
	SELECT
		customer_id,
		customer_name,
		customer_email,
		customer_city,
		customer_state,
		c.region,
		customer_status,
		ingested_at
	FROM (
		SELECT
			customer_id,
			customer_name,
			customer_email,
			customer_city,
			customer_state,
			customer_status,
			ingested_at,
			ROW_NUMBER() OVER (
				PARTITION BY customer_id
				ORDER BY ingested_at, transaction_id
			) AS rn
			FROM clean_classified
			WHERE customer_id IS NOT NULL
	) sub
	JOIN silver.state_region c ON c.state_ = sub.customer_state
	WHERE sub.rn = 1
	RETURNING customer_id
),

insert_merchant AS (
	INSERT INTO silver.merchants (
		merchant_id,
		merchant_name,
		merchant_category,
		merchant_city,
		merchant_state,
		merchant_region,
		merchant_status,
		first_seen_at
	)
	SELECT
		merchant_id,
		merchant_name,
		merchant_category,
		merchant_city,
		merchant_state,
		c.region,
		merchant_status,
		ingested_at
	FROM (
		SELECT
			merchant_id,
			merchant_name,
			merchant_category,
			merchant_city,
			merchant_state,
			merchant_status,
			ingested_at,
			ROW_NUMBER() OVER (
				PARTITION BY merchant_id
				ORDER BY ingested_at, transaction_id
			) AS rn
			FROM clean_classified						
	) sub
	JOIN silver.state_region c ON c.state_ = sub.merchant_state
	WHERE sub.rn = 1
	RETURNING merchant_id
),

insert_transaction AS (
	INSERT INTO silver.transactions (
		transaction_id,
		transaction_amount,
		transaction_at,
		ingested_at,
		transaction_status,
		payment_method_id,
		customer_id,
		merchant_id	
	)
	SELECT
		sub.transaction_id,
		sub.transaction_amount,
		sub.transaction_at,
		sub.ingested_at,
		sub.transaction_status,
		sub.payment_method_id,
		sub.customer_id,
		sub.merchant_id
	FROM (
		SELECT
			transaction_id,
			transaction_amount,
			transaction_at,
			ingested_at,
			transaction_status,
			payment_method_id,
			customer_id,
			merchant_id,
			rejection_reason,
			ROW_NUMBER() OVER (
				PARTITION BY transaction_id
				ORDER BY ingested_at
			) AS rn
		FROM clean_classified
	) sub
	JOIN insert_payment_method p ON p.payment_method_id = sub.payment_method_id
	JOIN insert_customer c ON c.customer_id = sub.customer_id
	JOIN insert_merchant m ON m.merchant_id = sub.merchant_id
	WHERE sub.rn = 1 AND sub.rejection_reason IS NULL
	RETURNING transaction_id
)

SELECT 
    (SELECT COUNT(*) FROM insert_rejected)			AS total_insert_rejected,
    (SELECT COUNT(*) FROM insert_payment_method)	AS total_insert_payment_method,
    (SELECT COUNT(*) FROM insert_customer) 		AS total_insert_customer,
	(SELECT COUNT(*) FROM insert_merchant) 		AS total_insert_merchant,
    (SELECT COUNT(*) FROM insert_transaction) 		AS total_inser_transaction;