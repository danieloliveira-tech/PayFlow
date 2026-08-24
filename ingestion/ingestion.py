import os
import json
from pathlib import Path
import psycopg
from dotenv import load_dotenv

current_folder = Path(__file__).parent
FOLDER = current_folder.parent / 'data' / 'incoming'

load_dotenv(current_folder.parent / ".env")

def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "payflow"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def main():
    processed_count = 0
    non_processed_count = 0
    global_row_count = 0

    for file_jsonl in sorted(FOLDER.glob("*.jsonl")):
        with get_connection() as conn:

            with conn.cursor() as cursor:               
                file_name = file_jsonl.name
                cursor.execute("SELECT file_name FROM pipeline.processed_files WHERE file_name = %s", (file_name,))
                already_processed = cursor.fetchone()
                if already_processed:
                    non_processed_count += 1
                    continue
                with file_jsonl.open("r", encoding="utf-8") as file:

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
                    processed_count += 1
                    global_row_count += row_count

    print(f"Total files processed: {processed_count}")
    print(f"Total files not processed: {non_processed_count}")
    print(f"Total lines processed: {global_row_count}")
            
        

if __name__ == "__main__":
    main()


