import json
import random
import re
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import (
    CUSTOMER_COUNT,
    DAYS,
    DUPLICATE_RATE,
    MAX_DAILY_TRANSACTIONS,
    MERCHANT_COUNT,
    MIN_DAILY_TRANSACTIONS,
    QUALITY_ERROR_RATE,
    SEED,
    START_DATE,
)
from data import (
    AMOUNT_RANGES,
    CATEGORIES,
    CATEGORY_WEIGHTS,
    FIRST_NAMES,
    LAST_NAMES,
    MERCHANT_PREFIXES,
    MERCHANT_SUFFIXES,
    PAYMENT_METHODS,
    REGIONS,
    SOURCE_FIELDS,
    STATE_DATA,
)

BRT = timezone(timedelta(hours=-3))


def slug(text):
    """Transforma um nome em uma parte simples de e-mail."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", ".", text.lower()).strip(".")
    return text


def pick_location():
    states = list(STATE_DATA.keys())
    weights = [STATE_DATA[state][2] for state in states]
    state = random.choices(states, weights=weights, k=1)[0]
    region, cities, _ = STATE_DATA[state]
    city = random.choice(cities)
    return city, state, region


def build_customers():
    customers = []

    for customer_id in range(1, CUSTOMER_COUNT + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        city, state, region = pick_location()
        status = random.choices(
            ["active", "inactive", "blocked"],
            weights=[92, 5, 3],
            k=1,
        )[0]

        customers.append(
            {
                "id": customer_id,
                "name": name,
                "email": f"{slug(name)}.{customer_id:04d}@example.com",
                "city": city,
                "state": state,
                "region": region,
                "status": status,
            }
        )

    return customers


def build_merchants():
    merchants = []

    # Garante ao menos um merchant de cada categoria.
    categories = CATEGORIES.copy()
    while len(categories) < MERCHANT_COUNT:
        categories.append(
            random.choices(
                CATEGORIES,
                weights=[CATEGORY_WEIGHTS[c] for c in CATEGORIES],
                k=1,
            )[0]
        )
    random.shuffle(categories)

    for merchant_id, category in enumerate(categories, start=1):
        city, state, region = pick_location()
        prefix = random.choice(MERCHANT_PREFIXES[category])
        suffix = random.choice(MERCHANT_SUFFIXES)

        merchants.append(
            {
                "id": merchant_id,
                "name": f"{prefix} {suffix} {merchant_id:03d}",
                "category": category,
                "city": city,
                "state": state,
                "region": region,
                "status": random.choices(["active", "inactive"], weights=[97, 3], k=1)[0],
            }
        )

    return merchants


def pick_hour():
    # Muito menos movimento na madrugada, mais durante o dia/noite.
    weights = [
        1, 1, 1, 1, 1, 2,
        4, 6, 7, 8, 9, 10,
        12, 12, 11, 10, 10, 11,
        13, 14, 14, 12, 8, 5,
    ]
    return random.choices(range(24), weights=weights, k=1)[0]


def pick_category(day, hour):
    weights = CATEGORY_WEIGHTS.copy()

    # Poucas regras visíveis e fáceis de explicar.
    if 11 <= hour <= 14 or 18 <= hour <= 21:
        weights["alimentacao"] += 12

    if 18 <= hour <= 23:
        weights["entretenimento"] += 8

    if day.weekday() < 5 and (7 <= hour <= 9 or 17 <= hour <= 19):
        weights["transporte"] += 8

    if day.weekday() >= 5:
        weights["supermercado"] += 5
        weights["entretenimento"] += 5

    return random.choices(
        CATEGORIES,
        weights=[weights[category] for category in CATEGORIES],
        k=1,
    )[0]


def pick_merchant(merchants, category, customer):
    candidates = [m for m in merchants if m["category"] == category]

    # Na maioria das vezes tenta usar um merchant do mesmo estado.
    if random.random() < 0.70:
        local = [m for m in candidates if m["state"] == customer["state"]]
        if local:
            candidates = local

    return random.choice(candidates)


def generate_amount(category):
    low, high = AMOUNT_RANGES[category]
    return round(random.uniform(low, high), 2)


def pick_payment_method(amount):
    if amount < 50:
        payment_type = random.choices(
            ["pix", "debit_card", "credit_card"], weights=[45, 40, 15], k=1
        )[0]
    elif amount < 200:
        payment_type = random.choices(
            ["pix", "debit_card", "credit_card"], weights=[35, 30, 35], k=1
        )[0]
    elif amount < 800:
        payment_type = random.choices(
            ["pix", "debit_card", "credit_card"], weights=[25, 20, 55], k=1
        )[0]
    else:
        payment_type = random.choices(
            ["pix", "debit_card", "credit_card"], weights=[15, 10, 75], k=1
        )[0]

    candidates = [p for p in PAYMENT_METHODS if p["type"] == payment_type]
    return random.choice(candidates)


def pick_transaction_status(customer, merchant, payment_method):
    if customer["status"] != "active":
        return "declined"

    if merchant["status"] != "active":
        return "declined"

    # Cartão possui uma taxa de recusa um pouco maior que Pix.
    if payment_method["type"] == "credit_card":
        weights = [88, 8, 2, 2]
    elif payment_method["type"] == "debit_card":
        weights = [91, 5, 2, 2]
    else:
        weights = [93, 3, 2, 2]

    return random.choices(
        ["approved", "declined", "pending", "refunded"],
        weights=weights,
        k=1,
    )[0]


def make_clean_record(transaction_id, day, customers, merchants):
    customer = random.choice(customers)
    hour = pick_hour()
    minute = random.randint(0, 59)
    transaction_at = datetime(
        day.year,
        day.month,
        day.day,
        hour,
        minute,
        tzinfo=BRT,
    )

    category = pick_category(day, hour)
    merchant = pick_merchant(merchants, category, customer)
    amount = generate_amount(category)
    payment = pick_payment_method(amount)
    status = pick_transaction_status(customer, merchant, payment)

    return {
        "transaction_id": transaction_id,
        "transaction_at": transaction_at.isoformat(timespec="minutes"),
        "transaction_amount": amount,
        "transaction_status": status,
        "customer_id": customer["id"],
        "customer_name": customer["name"],
        "customer_email": customer["email"],
        "customer_city": customer["city"],
        "customer_state": customer["state"],
        "customer_region": customer["region"],
        "customer_status": customer["status"],
        "merchant_id": merchant["id"],
        "merchant_name": merchant["name"],
        "merchant_category": merchant["category"],
        "merchant_city": merchant["city"],
        "merchant_state": merchant["state"],
        "merchant_region": merchant["region"],
        "merchant_status": merchant["status"],
        "payment_method_id": payment["id"],
        "payment_method_name": payment["name"],
        "payment_method_type": payment["type"],
        "payment_method_brand": payment["brand"],
    }


def add_quality_problem(record):
    """Aplica no máximo um problema de qualidade à linha."""
    if random.random() >= QUALITY_ERROR_RATE:
        return None

    problem = random.choice(
        [
            "case_whitespace",
            "email_format",
            "region_mismatch",
            "nonpositive_amount",
            "null_transaction_id",
            "null_customer_id",
            "unknown_status",
            "invalid_payment_type",
        ]
    )

    if problem == "case_whitespace":
        field = random.choice(
            [
                "transaction_status",
                "customer_city",
                "customer_state",
                "customer_region",
                "customer_status",
                "merchant_category",
                "merchant_city",
                "merchant_state",
                "merchant_region",
                "merchant_status",
                "payment_method_name",
                "payment_method_type",
            ]
        )
        mode = random.choice(["upper", "lower", "spaces"])
        if mode == "upper":
            record[field] = record[field].upper()
        elif mode == "lower":
            record[field] = record[field].lower()
        else:
            record[field] = f" {record[field]} "

    elif problem == "email_format":
        record["customer_email"] = f" {record['customer_email'].upper()} "

    elif problem == "region_mismatch":
        field = random.choice(["customer_region", "merchant_region"])
        current = record[field]
        record[field] = random.choice([region for region in REGIONS if region != current])

    elif problem == "nonpositive_amount":
        if random.random() < 0.5:
            record["transaction_amount"] = 0
        else:
            record["transaction_amount"] = -record["transaction_amount"]

    elif problem == "null_transaction_id":
        record["transaction_id"] = None

    elif problem == "null_customer_id":
        record["customer_id"] = None

    elif problem == "unknown_status":
        record["transaction_status"] = "unknown"

    elif problem == "invalid_payment_type":
        record["payment_method_type"] = random.choice(
            ["card", "credit", "debit", "wallet", "pix_card"]
        )

    return problem


def validate_record(record, day):
    if list(record.keys()) != SOURCE_FIELDS:
        raise ValueError("Registro com campos ausentes, extras ou fora da ordem esperada.")

    if not record["transaction_at"].startswith(day.isoformat()):
        raise ValueError("transaction_at não pertence ao arquivo diário correto.")


def daily_volume(day):
    volume = random.randint(MIN_DAILY_TRANSACTIONS, MAX_DAILY_TRANSACTIONS)

    # Pequena diferença por dia da semana, sem tabela congelada.
    if day.weekday() in (4, 5):  # sexta/sábado
        volume += random.randint(50, 150)
    elif day.weekday() == 6:  # domingo
        volume -= random.randint(50, 120)

    return max(1000, volume)


def generate_dataset(output_dir):
    random.seed(SEED)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Evita deixar lotes antigos na pasta quando o período for alterado.
    for old_file in output_path.glob("transactions_*.jsonl"):
        old_file.unlink()

    customers = build_customers()
    merchants = build_merchants()

    transaction_id = 1
    total_rows = 0
    total_transactions = 0
    duplicate_count = 0
    problem_counts = Counter()

    for offset in range(DAYS):
        day = START_DATE + timedelta(days=offset)
        rows = []

        for _ in range(daily_volume(day)):
            record = make_clean_record(
                transaction_id=transaction_id,
                day=day,
                customers=customers,
                merchants=merchants,
            )
            transaction_id += 1
            total_transactions += 1

            clean_copy = record.copy()
            problem = add_quality_problem(record)
            if problem:
                problem_counts[problem] += 1

            validate_record(record, day)
            rows.append(record)

            # Duplicata só é criada quando a própria linha permaneceu limpa.
            if problem is None and random.random() < DUPLICATE_RATE:
                validate_record(clean_copy, day)
                rows.append(clean_copy)
                duplicate_count += 1

        random.shuffle(rows)

        file_path = output_path / f"transactions_{day.isoformat()}.jsonl"
        with file_path.open("w", encoding="utf-8") as file:
            for record in rows:
                file.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
                file.write("\n")

        total_rows += len(rows)

    return {
        "customers": len(customers),
        "merchants": len(merchants),
        "payment_methods": len(PAYMENT_METHODS),
        "days": DAYS,
        "transactions": total_transactions,
        "rows": total_rows,
        "duplicates": duplicate_count,
        "quality_problems": dict(problem_counts),
        "output_dir": str(output_path.resolve()),
    }
