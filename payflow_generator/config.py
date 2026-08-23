from datetime import date

SEED = 20260101
START_DATE = date(2026, 1, 1)
DAYS = 45

CUSTOMER_COUNT = 2000
MERCHANT_COUNT = 250

MIN_DAILY_TRANSACTIONS = 1300
MAX_DAILY_TRANSACTIONS = 1750

# Aproximadamente 3% das transações recebem um problema de qualidade.
QUALITY_ERROR_RATE = 0.03

# Aproximadamente 0,2% das linhas são duplicadas.
DUPLICATE_RATE = 0.002

OUTPUT_DIR = "output"
