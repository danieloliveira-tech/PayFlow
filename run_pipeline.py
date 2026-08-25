import os
import subprocess
import sys
import time
from pathlib import Path

import psycopg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
SQL_DIR = PROJECT_ROOT / "sql"
DATA_INCOMING_DIR = PROJECT_ROOT / "data" / "incoming"

GENERATOR_SCRIPT = PROJECT_ROOT / "generator" / "generate.py"
INGESTION_SCRIPT = PROJECT_ROOT / "ingestion" / "ingestion.py"
ANALYTICS_SCRIPT = PROJECT_ROOT / "analytics" / "run_analysis.py"

# Mantém os nomes atuais dos seus arquivos.
# 05 e 09 são scripts de carga, então rodam nas fases corretas do pipeline.
STRUCTURE_SQL_FILES = [
    "01_create_schemas.sql",
    "02_create_bronze_tables.sql",
    "03_create_pipeline_tables.sql",
    "04_create_silver_tables.sql",
    "06_insert_region_table.sql",
    "07_create_gold_tables.sql",
    "08_create_gold_index.sql",
]

SILVER_LOAD_SQL = "05_CTE_insert_silver_tables.sql"
GOLD_LOAD_SQL = "09_load_gold.sql"

load_dotenv(PROJECT_ROOT / ".env")


def print_step(message):
    print(f"\n{'=' * 70}")
    print(message)
    print(f"{'=' * 70}")


def get_connection(*, autocommit=False):
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5433"),
        dbname=os.getenv("POSTGRES_DB", "payflow"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
        autocommit=autocommit,
    )


def run_command(command, *, cwd=PROJECT_ROOT):
    subprocess.run(command, cwd=cwd, check=True)


def start_postgres():
    print_step("1/7 - Iniciando PostgreSQL com Docker")
    run_command(["docker", "compose", "up", "-d"])


def wait_for_postgres(max_attempts=30, delay_seconds=2):
    print("Aguardando PostgreSQL ficar disponível...")

    for attempt in range(1, max_attempts + 1):
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1;")
                    cursor.fetchone()

            print("PostgreSQL disponível.")
            return

        except psycopg.OperationalError:
            print(f"Tentativa {attempt}/{max_attempts}...")
            time.sleep(delay_seconds)

    raise RuntimeError(
        "Não foi possível conectar ao PostgreSQL. "
        "Confira 'docker compose logs postgres' e o arquivo .env."
    )


def execute_sql_file(filename):
    path = SQL_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"SQL não encontrado: {path}")

    print(f"Executando {filename}...")
    sql = path.read_text(encoding="utf-8")

    # Os scripts 05 e 09 já possuem BEGIN/COMMIT próprios.
    with get_connection(autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)


def initialize_database():
    print_step("2/7 - Criando estrutura do banco")

    for filename in STRUCTURE_SQL_FILES:
        execute_sql_file(filename)

    print("Estrutura do banco pronta.")


def generate_data():
    print_step("3/7 - Gerando dados sintéticos")

    DATA_INCOMING_DIR.mkdir(parents=True, exist_ok=True)

    if not GENERATOR_SCRIPT.exists():
        raise FileNotFoundError(
            f"Gerador não encontrado: {GENERATOR_SCRIPT}"
        )

    run_command(
        [
            sys.executable,
            str(GENERATOR_SCRIPT),
            "--output-dir",
            str(DATA_INCOMING_DIR),
        ],
        cwd=PROJECT_ROOT,
    )

    print(f"Dados disponíveis em: {DATA_INCOMING_DIR}")


def run_ingestion():
    print_step("4/7 - Ingestão incremental: JSONL -> Bronze")

    if not INGESTION_SCRIPT.exists():
        raise FileNotFoundError(
            f"Script de ingestão não encontrado: {INGESTION_SCRIPT}\n"
            "Se o seu arquivo tiver outro nome, altere INGESTION_SCRIPT "
            "no início de run_pipeline.py."
        )

    run_command(
        [sys.executable, str(INGESTION_SCRIPT)],
        cwd=PROJECT_ROOT,
    )


def load_silver():
    print_step("5/7 - Transformação incremental: Bronze -> Silver")
    execute_sql_file(SILVER_LOAD_SQL)


def load_gold():
    print_step("6/7 - Transformação incremental: Silver -> Gold")
    execute_sql_file(GOLD_LOAD_SQL)


def run_analytics():
    print_step("7/7 - Executando análises da Gold")

    if not ANALYTICS_SCRIPT.exists():
        raise FileNotFoundError(
            f"Script de analytics não encontrado: {ANALYTICS_SCRIPT}"
        )

    run_command(
        [sys.executable, str(ANALYTICS_SCRIPT)],
        cwd=PROJECT_ROOT,
    )


def show_summary():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM bronze.transactions_raw;")
            bronze_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM silver.transactions;")
            silver_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM silver.rejected_transactions;")
            rejected_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM gold.fact_transaction;")
            gold_count = cursor.fetchone()[0]

    print_step("Pipeline concluído")
    print(f"Bronze - registros físicos : {bronze_count}")
    print(f"Silver - transações válidas: {silver_count}")
    print(f"Silver - rejeitadas         : {rejected_count}")
    print(f"Gold   - fatos              : {gold_count}")
    print("\nGráficos gerados em analytics/outputs/")


def main():
    try:
        start_postgres()
        wait_for_postgres()
        initialize_database()
        generate_data()
        run_ingestion()
        load_silver()
        load_gold()
        run_analytics()
        show_summary()

    except subprocess.CalledProcessError as exc:
        print(
            f"\nERRO: um comando externo terminou com código {exc.returncode}.",
            file=sys.stderr,
        )
        sys.exit(exc.returncode)

    except Exception as exc:
        print(f"\nERRO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
