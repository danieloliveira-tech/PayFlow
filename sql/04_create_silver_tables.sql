CREATE TABLE IF NOT EXISTS silver.customers (
	customer_id		BIGINT PRIMARY KEY,
	customer_name	VARCHAR(100) NOT NULL,
	customer_email	VARCHAR(150) NOT NULL,
	customer_city	VARCHAR(50) NOT NULL,
	customer_state	VARCHAR(50) NOT NULL,
	customer_region	VARCHAR(30) NOT NULL,
	customer_status	VARCHAR(30)	NOT NULL, CHECK(customer_status IN ('active', 'inactive', 'blocked')),
	first_seen_at	TIMESTAMPTZ(0) NOT NULL
);

CREATE TABLE IF NOT EXISTS silver.merchants (
	merchant_id			BIGINT PRIMARY KEY,
	merchant_name		VARCHAR(100) NOT NULL,
	merchant_category	VARCHAR(100) NOT NULL,
	merchant_city		VARCHAR(50) NOT NULL,
	merchant_state		VARCHAR(50) NOT NULL,
	merchant_region		VARCHAR(30) NOT NULL,
	merchant_status		VARCHAR(30)	NOT NULL, CHECK(merchant_status IN ('active', 'inactive')),
	first_seen_at		TIMESTAMPTZ(0) NOT NULL
);

CREATE TABLE IF NOT EXISTS silver.payment_methods (
	payment_method_id		BIGINT PRIMARY KEY,
	payment_method_name		VARCHAR(30) NOT NULL,
	payment_method_type		VARCHAR(15) NOT NULL,
	payment_method_brand	VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS silver.transactions (
	transaction_id		BIGINT PRIMARY KEY,
	transaction_amount	NUMERIC(15, 2) NOT NULL, CHECK(transaction_amount > 0),
	transaction_at		TIMESTAMPTZ(0) NOT NULL,
	ingested_at			TIMESTAMPTZ(0) NOT NULL,
	transaction_status	VARCHAR(15) NOT NULL, CHECK(transaction_status IN ('approved', 'declined', 'pending', 'refunded')),
	payment_method_id	BIGINT,
	customer_id			BIGINT,
	merchant_id			BIGINT,

	FOREIGN KEY(payment_method_id) REFERENCES silver.payment_methods(payment_method_id)
		ON UPDATE CASCADE,
		
	FOREIGN KEY(customer_id) REFERENCES silver.customers(customer_id)
		ON UPDATE CASCADE,

	FOREIGN KEY(merchant_id) REFERENCES silver.merchants(merchant_id)
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS silver.rejected_transactions (
	rejected_id			BIGSERIAL PRIMARY KEY,
	transaction_id		BIGINT,
	ingested_at			TIMESTAMPTZ(0),
	source_file			VARCHAR(100),
	rejection_reason	VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS silver.state_region (
	state_	VARCHAR(2) PRIMARY KEY,
	region	VARCHAR(15)
);
