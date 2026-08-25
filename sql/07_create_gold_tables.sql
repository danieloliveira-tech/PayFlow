CREATE TABLE IF NOT EXISTS gold.dim_datetime (
    datetime_pk         BIGSERIAL PRIMARY KEY,
    full_datetime       TIMESTAMP(0) NOT NULL UNIQUE,
    hour                SMALLINT NOT NULL CHECK (hour BETWEEN 0 AND 23),
    day                 SMALLINT NOT NULL CHECK (day BETWEEN 1 AND 31),
    month               SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
    year                SMALLINT NOT NULL,
    day_of_the_week     SMALLINT NOT NULL CHECK (day_of_the_week BETWEEN 1 AND 7),
    quarter             SMALLINT NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    semester            SMALLINT NOT NULL CHECK (semester BETWEEN 1 AND 2)
);


CREATE TABLE IF NOT EXISTS gold.dim_payment (
    payment_pk              BIGSERIAL PRIMARY KEY,
    payment_method_id       BIGINT NOT NULL UNIQUE,
    payment_method_name     VARCHAR(30) NOT NULL,
    payment_method_type     VARCHAR(15) NOT NULL,
    payment_method_brand    VARCHAR(30)
);


CREATE TABLE IF NOT EXISTS gold.dim_merchant (
    merchant_pk         BIGSERIAL PRIMARY KEY,
    merchant_id         BIGINT NOT NULL UNIQUE,
    merchant_name       VARCHAR(100) NOT NULL,
    merchant_category   VARCHAR(100) NOT NULL,
    merchant_status     VARCHAR(30) NOT NULL CHECK (merchant_status IN ('active', 'inactive'))
);


CREATE TABLE IF NOT EXISTS gold.dim_location (
    location_pk     BIGSERIAL PRIMARY KEY,
    city            VARCHAR(50) NOT NULL,
    state           VARCHAR(50) NOT NULL,
    region          VARCHAR(30) NOT NULL,
    UNIQUE (city, state, region)
);

CREATE TABLE IF NOT EXISTS gold.fact_transaction (
    transaction_pk          BIGINT PRIMARY KEY,
    datetime_pk             BIGINT NOT NULL,
    payment_pk              BIGINT NOT NULL,
    merchant_pk             BIGINT NOT NULL,
    merchant_location_pk    BIGINT NOT NULL,
    customer_location_pk    BIGINT NOT NULL,
    customer_id             BIGINT NOT NULL,
    transaction_status      VARCHAR(15) NOT NULL CHECK (transaction_status IN ('approved','declined','pending','refunded')),
    customer_status         VARCHAR(30) NOT NULL CHECK (customer_status IN ('active','inactive','blocked')),
    amount                  NUMERIC(15, 2) NOT NULL CHECK (amount > 0),

    FOREIGN KEY (datetime_pk)
        REFERENCES gold.dim_datetime(datetime_pk),

    FOREIGN KEY (payment_pk)
        REFERENCES gold.dim_payment(payment_pk),

    FOREIGN KEY (merchant_pk)
        REFERENCES gold.dim_merchant(merchant_pk),

    FOREIGN KEY (merchant_location_pk)
        REFERENCES gold.dim_location(location_pk),

    FOREIGN KEY (customer_location_pk)
        REFERENCES gold.dim_location(location_pk)
);