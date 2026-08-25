# Catálogo geográfico pequeno, mas cobrindo o Brasil inteiro.
# Os pesos por estado são propositalmente desiguais para concentrar mais
# clientes e merchants nos estados mais populosos.

STATE_DATA = {
    "AC": ("Norte", ["Rio Branco", "Cruzeiro do Sul"], 1),
    "AL": ("Nordeste", ["Maceió", "Arapiraca"], 2),
    "AP": ("Norte", ["Macapá", "Santana"], 1),
    "AM": ("Norte", ["Manaus", "Parintins"], 3),
    "BA": ("Nordeste", ["Salvador", "Feira de Santana", "Vitória da Conquista"], 8),
    "CE": ("Nordeste", ["Fortaleza", "Caucaia", "Juazeiro do Norte"], 5),
    "DF": ("Centro-Oeste", ["Brasília"], 2),
    "ES": ("Sudeste", ["Vitória", "Vila Velha", "Serra"], 3),
    "GO": ("Centro-Oeste", ["Goiânia", "Aparecida de Goiânia", "Anápolis"], 4),
    "MA": ("Nordeste", ["São Luís", "Imperatriz"], 4),
    "MT": ("Centro-Oeste", ["Cuiabá", "Rondonópolis"], 2),
    "MS": ("Centro-Oeste", ["Campo Grande", "Dourados"], 2),
    "MG": ("Sudeste", ["Belo Horizonte", "Uberlândia", "Juiz de Fora", "Contagem"], 11),
    "PA": ("Norte", ["Belém", "Ananindeua", "Santarém"], 5),
    "PB": ("Nordeste", ["João Pessoa", "Campina Grande"], 3),
    "PR": ("Sul", ["Curitiba", "Londrina", "Maringá"], 7),
    "PE": ("Nordeste", ["Recife", "Jaboatão dos Guararapes", "Caruaru"], 5),
    "PI": ("Nordeste", ["Teresina", "Parnaíba"], 2),
    "RJ": ("Sudeste", ["Rio de Janeiro", "Niterói", "São Gonçalo"], 9),
    "RN": ("Nordeste", ["Natal", "Mossoró"], 2),
    "RS": ("Sul", ["Porto Alegre", "Caxias do Sul", "Canoas"], 6),
    "RO": ("Norte", ["Porto Velho", "Ji-Paraná"], 1),
    "RR": ("Norte", ["Boa Vista", "Rorainópolis"], 1),
    "SC": ("Sul", ["Florianópolis", "Joinville", "Blumenau"], 5),
    "SP": ("Sudeste", ["São Paulo", "Guarulhos", "Campinas", "São Bernardo do Campo"], 24),
    "SE": ("Nordeste", ["Aracaju", "Lagarto"], 2),
    "TO": ("Norte", ["Palmas", "Araguaína"], 1),
}

REGIONS = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

FIRST_NAMES = [
    "Ana", "Beatriz", "Bruno", "Camila", "Carlos", "Daniel", "Eduarda",
    "Felipe", "Fernanda", "Gabriel", "Gustavo", "Isabela", "João",
    "Juliana", "Larissa", "Lucas", "Mariana", "Mateus", "Patrícia",
    "Rafael", "Renata", "Rodrigo", "Sofia", "Thiago", "Vanessa",
]

LAST_NAMES = [
    "Almeida", "Barbosa", "Cardoso", "Carvalho", "Costa", "Ferreira",
    "Gomes", "Lima", "Martins", "Mendes", "Oliveira", "Pereira",
    "Ribeiro", "Rocha", "Santana", "Santos", "Silva", "Souza",
]

CATEGORIES = [
    "supermercado",
    "alimentacao",
    "farmacia",
    "transporte",
    "combustivel",
    "eletronicos",
    "vestuario",
    "entretenimento",
    "serviços",
]

# Peso base simples para a frequência das categorias.
CATEGORY_WEIGHTS = {
    "supermercado": 18,
    "alimentacao": 24,
    "farmacia": 10,
    "transporte": 15,
    "combustivel": 9,
    "eletronicos": 3,
    "vestuario": 8,
    "entretenimento": 6,
    "serviços": 7,
}

# A categoria influencia o valor, sem tentar simular uma distribuição financeira sofisticada.
AMOUNT_RANGES = {
    "transporte": (5, 80),
    "alimentacao": (15, 180),
    "farmacia": (15, 300),
    "supermercado": (40, 500),
    "combustivel": (80, 400),
    "vestuario": (50, 800),
    "serviços": (50, 1500),
    "eletronicos": (200, 5000),
    "entretenimento": (20, 300),
}

MERCHANT_PREFIXES = {
    "supermercado": ["Mercado", "Supermercado"],
    "alimentacao": ["Restaurante", "Café", "Bistrô"],
    "farmacia": ["Farmácia", "Drogaria"],
    "transporte": ["Mobilidade", "Transportes"],
    "combustivel": ["Auto Posto", "Posto"],
    "eletronicos": ["Tech", "Eletrônicos"],
    "vestuario": ["Moda", "Vestuário"],
    "entretenimento": ["Cinema", "Diversão"],
    "serviços": ["Serviços", "Soluções"],
}

MERCHANT_SUFFIXES = [
    "Aurora", "Central", "Horizonte", "Integra", "Nova Era", "Primavera",
    "Estrela", "Vila Nova", "Brasil", "Ponto Certo", "Serra", "Litoral",
]

PAYMENT_METHODS = [
    {"id": 1, "name": "Pix", "type": "pix", "brand": None},
    {"id": 2, "name": "Visa Crédito", "type": "credit_card", "brand": "Visa"},
    {"id": 3, "name": "Mastercard Crédito", "type": "credit_card", "brand": "Mastercard"},
    {"id": 4, "name": "Elo Crédito", "type": "credit_card", "brand": "Elo"},
    {"id": 5, "name": "American Express Crédito", "type": "credit_card", "brand": "American Express"},
    {"id": 6, "name": "Visa Débito", "type": "debit_card", "brand": "Visa"},
    {"id": 7, "name": "Mastercard Débito", "type": "debit_card", "brand": "Mastercard"},
    {"id": 8, "name": "Elo Débito", "type": "debit_card", "brand": "Elo"},
]

SOURCE_FIELDS = [
    "transaction_id",
    "transaction_at",
    "transaction_amount",
    "transaction_status",
    "customer_id",
    "customer_name",
    "customer_email",
    "customer_city",
    "customer_state",
    "customer_region",
    "customer_status",
    "merchant_id",
    "merchant_name",
    "merchant_category",
    "merchant_city",
    "merchant_state",
    "merchant_region",
    "merchant_status",
    "payment_method_id",
    "payment_method_name",
    "payment_method_type",
    "payment_method_brand",
]
