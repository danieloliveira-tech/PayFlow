import argparse

from config import OUTPUT_DIR, SEED
from generator import generate_dataset


def main():
    parser = argparse.ArgumentParser(
        description="Gera arquivos JSONL sintéticos para o projeto Payflow."
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR,
        help=f"Pasta de saída. Padrão: {OUTPUT_DIR}",
    )
    args = parser.parse_args()

    summary = generate_dataset(args.output_dir)

    print("\nPayflow dataset gerado com sucesso.")
    print(f"Seed: {SEED}")
    print(f"Pasta de saída: {summary['output_dir']}")
    print(f"Arquivos diários: {summary['days']}")
    print(f"Customers: {summary['customers']}")
    print(f"Merchants: {summary['merchants']}")
    print(f"Payment methods: {summary['payment_methods']}")
    print(f"Transações novas: {summary['transactions']:,}".replace(",", "."))
    print(f"Linhas físicas: {summary['rows']:,}".replace(",", "."))
    print(f"Duplicatas adicionadas: {summary['duplicates']}")
    print("Problemas de qualidade:")
    for problem, count in sorted(summary["quality_problems"].items()):
        print(f"  {problem}: {count}")


if __name__ == "__main__":
    main()
