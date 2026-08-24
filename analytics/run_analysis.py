import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import psycopg
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
QUERIES_DIR = BASE_DIR / "queries"
OUTPUTS_DIR = BASE_DIR / "outputs"

load_dotenv(BASE_DIR.parent / ".env")


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "payflow"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def load_query(filename):
    return (QUERIES_DIR / filename).read_text(encoding="utf-8")


def execute_query(conn, filename):
    query = load_query(filename)

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column.name for column in cursor.description]

    return pd.DataFrame(rows, columns=columns)


def save_transactions_by_hour(df):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df["hour"], df["transaction_count"])
    ax.set_title("Transações por hora")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Quantidade de transações")
    ax.set_xticks(range(24))
    fig.tight_layout()
    fig.savefig(OUTPUTS_DIR / "transactions_by_hour.png", dpi=150)
    plt.close(fig)


def save_approval_rate_by_payment(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df["payment_method_type"], df["approval_rate_pct"])
    ax.set_title("Taxa de aprovação por tipo de pagamento")
    ax.set_xlabel("Tipo de pagamento")
    ax.set_ylabel("Taxa de aprovação (%)")
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(OUTPUTS_DIR / "approval_rate_by_payment.png", dpi=150)
    plt.close(fig)


def save_merchant_category_metrics(df):
    ordered = df.sort_values("average_ticket")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(ordered["merchant_category"], ordered["average_ticket"])
    ax.set_title("Ticket médio por categoria de merchant")
    ax.set_xlabel("Ticket médio (R$)")
    ax.set_ylabel("Categoria")
    fig.tight_layout()
    fig.savefig(OUTPUTS_DIR / "merchant_category_metrics.png", dpi=150)
    plt.close(fig)


def save_transactions_by_region(df):
    matrix = df.pivot(
        index="customer_region",
        columns="merchant_region",
        values="transaction_count",
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(9, 6))
    image = ax.imshow(matrix.values, aspect="auto")

    ax.set_title("Transações: região do cliente x região do merchant")
    ax.set_xlabel("Região do merchant")
    ax.set_ylabel("Região do cliente")
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index)

    for row_index in range(len(matrix.index)):
        for column_index in range(len(matrix.columns)):
            ax.text(
                column_index,
                row_index,
                int(matrix.iloc[row_index, column_index]),
                ha="center",
                va="center",
            )

    fig.colorbar(image, ax=ax, label="Quantidade de transações")
    fig.tight_layout()
    fig.savefig(OUTPUTS_DIR / "transactions_by_region.png", dpi=150)
    plt.close(fig)


def save_refund_rate_by_category(df):
    ordered = df.sort_values("refund_rate_pct")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(ordered["merchant_category"], ordered["refund_rate_pct"])
    ax.set_title("Taxa de refund por categoria de merchant")
    ax.set_xlabel("Taxa de refund (%)")
    ax.set_ylabel("Categoria")
    fig.tight_layout()
    fig.savefig(OUTPUTS_DIR / "refund_rate_by_category.png", dpi=150)
    plt.close(fig)


def main():
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    analyses = [
        ("transactions_by_hour.sql", save_transactions_by_hour),
        ("approval_rate_by_payment.sql", save_approval_rate_by_payment),
        ("merchant_category_metrics.sql", save_merchant_category_metrics),
        ("transactions_by_region.sql", save_transactions_by_region),
        ("refund_rate_by_category.sql", save_refund_rate_by_category),
    ]

    with get_connection() as conn:
        for query_file, plot_function in analyses:
            print(f"Executando {query_file}...")
            dataframe = execute_query(conn, query_file)

            if dataframe.empty:
                print("  Nenhum dado retornado; gráfico ignorado.")
                continue

            plot_function(dataframe)
            print("  Gráfico salvo.")

    print(f"\nAnálises concluídas. Arquivos em: {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
