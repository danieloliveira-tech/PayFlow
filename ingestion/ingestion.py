import json
from pathlib import Path
import psycopg

current_folder = Path(__file__).parent

FILE_PATH = current_folder.parent / 'data' / 'incoming' / 'transactions_2026-01-01.jsonl'

def main():
    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="payflow",
        user="postgres",
        password="senha",
    ) as conn:

        with conn.cursor() as cursor:

            with FILE_PATH.open("r", encoding="utf-8") as file:
                file_name = FILE_PATH.name
                row_count = 0
                for line in file:
                    record = json.loads(line)
                    record["source_file"] = file_name
                    values = list(record.values())
                    query = """
                            INSERT INTO bronze.transactions_raw (transaction_id, transaction_at, transaction_amount, transaction_status, customer_id, customer_name, customer_email, customer_city, customer_state, customer_region, customer_status, merchant_id, merchant_name, merchant_category, merchant_city, merchant_state, merchant_region, merchant_status, payment_method_id, payment_method_name, payment_method_type, payment_method_brand, source_file)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """

                    cursor.execute(query, values)
                    row_count += 1
                sql = "INSERT INTO pipeline.processed_files (file_name, row_count) VALUES (%s, %s)"
                cursor.execute(sql, (file_name, row_count))

        

if __name__ == "__main__":
    main()


