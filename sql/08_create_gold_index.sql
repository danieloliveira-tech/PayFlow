CREATE INDEX IF NOT EXISTS idx_fact_transaction_datetime ON gold.fact_transaction(datetime_pk);

CREATE INDEX IF NOT EXISTS idx_fact_transaction_payment ON gold.fact_transaction(payment_pk);

CREATE INDEX IF NOT EXISTS idx_fact_transaction_merchant ON gold.fact_transaction(merchant_pk);

CREATE INDEX IF NOT EXISTS idx_fact_transaction_customer ON gold.fact_transaction(customer_id);

CREATE INDEX IF NOT EXISTS idx_fact_transaction_customer_location ON gold.fact_transaction(customer_location_pk);

CREATE INDEX IF NOT EXISTS idx_fact_transaction_merchant_location ON gold.fact_transaction(merchant_location_pk);