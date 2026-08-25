CREATE TABLE IF NOT EXISTS pipeline.processed_files (
	file_name		VARCHAR(100) PRIMARY KEY,
	processed_at	TIMESTAMPTZ(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
	row_count		BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline.silver_processed_files (
    file_name       VARCHAR(100) PRIMARY KEY,
    processed_at    TIMESTAMPTZ(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
);