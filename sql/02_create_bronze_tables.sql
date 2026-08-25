-- criação da tabela com dados sujos na camada bronze
CREATE TABLE IF NOT EXISTS bronze.transactions_raw (
	transaction_id		BIGINT,
	transaction_at		TIMESTAMPTZ(0),
	transaction_amount	NUMERIC(15, 2),
	transaction_status	VARCHAR(15),

	customer_id			BIGINT,
	customer_name		VARCHAR(100),
	customer_email		VARCHAR(150),
	customer_city		VARCHAR(50),
	customer_state		VARCHAR(50),
	customer_region		VARCHAR(30),
	customer_status		VARCHAR(30),

	merchant_id			BIGINT,
	merchant_name		VARCHAR(100),
	merchant_category	VARCHAR(100),
	merchant_city		VARCHAR(50),
	merchant_state		VARCHAR(50),
	merchant_region		VARCHAR(30),
	merchant_status		VARCHAR(30),

	payment_method_id		BIGINT,
	payment_method_name		VARCHAR(30),
	payment_method_type		VARCHAR(15),
	payment_method_brand	VARCHAR(30),

	source_file		VARCHAR(100),
	ingested_at		TIMESTAMPTZ(0) DEFAULT CURRENT_TIMESTAMP
);