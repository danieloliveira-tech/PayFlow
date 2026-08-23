# Payflow Generator

Gerador sintético de dados para alimentar a camada Bronze de um projeto de engenharia de dados.

O foco não é construir um simulador financeiro sofisticado; é produzir uma fonte plausível, desnormalizada e levemente suja para depois trabalhar ingestão, transformação, qualidade e modelagem.

## O que ele tem

- 2.000 clientes estáveis e reutilizados entre transações;
- 250 merchants estáveis e reutilizados;
- 8 métodos de pagamento fixos;
- 45 arquivos diários;
- IDs de transação globalmente únicos e sequenciais;
- BRT / UTC-3, com precisão de minuto;
- merchant_category influenciando aproximadamente o valor;
- compras maiores usando crédito com mais frequência;
- customer `inactive`/`blocked` e merchant `inactive` sempre gerando `declined`;
- pequenas correlações de horário, como alimentação nas refeições e entretenimento à noite;
- distribuição geográfica desigual no Brasil;
- seed fixa para reprodutibilidade;
- alguns problemas de qualidade controlados;
- JSONL desnormalizado com os 22 campos definidos pelo projeto.

## O que é simplificado

Não existem:

- pesos lognormais de atividade/popularidade;
- dezenas de distribuições congeladas;
- contagem exata de transações por dia;
- orçamento exato de cada tipo de erro;
- múltiplos RNGs independentes;
- arquitetura com muitas camadas e classes;
- bateria estatística de validações.

O gerador usa apenas a biblioteca padrão do Python.

## Estrutura

```text
payflow-generator-simple/
├── generate.py   # ponto de entrada
├── config.py     # quantidades, datas, seed e taxas
├── data.py       # catálogos e faixas de valores
├── generator.py  # toda a lógica de geração
└── README.md
```

### `generate.py`

É o arquivo que você executa. Ele chama o gerador e imprime um resumo.

### `config.py`

Contém as configurações que provavelmente você mudaria primeiro: seed, data inicial, número de dias, quantidade de customers/merchants e taxas de sujeira.

### `data.py`

Contém dados estáticos: estados/cidades, categorias, faixas de preço, nomes e métodos de pagamento.

### `generator.py`

Contém a lógica propriamente dita. A ordem principal é:

```text
criar customers
criar merchants
para cada dia:
    definir volume aproximado
    gerar transações
    aplicar pequena sujeira
    adicionar algumas duplicatas
    embaralhar
    escrever JSONL
```

## Como executar

Requer Python 3.11+.

Na pasta do projeto:

```bash
python generate.py
```

Por padrão os arquivos são criados em:

```text
./output/
```

Você verá:

```text
output/
├── transactions_2026-01-01.jsonl
├── transactions_2026-01-02.jsonl
├── ...
└── transactions_2026-02-14.jsonl
```

Para escolher outra pasta:

```bash
python generate.py --output-dir ./dados/bronze-input
```

Não existem dependências externas, `requirements.txt` ou instalação de pacote.

## Schema de cada linha

Cada linha possui exatamente:

```text
transaction_id
transaction_at
transaction_amount
transaction_status
customer_id
customer_name
customer_email
customer_city
customer_state
customer_region
customer_status
merchant_id
merchant_name
merchant_category
merchant_city
merchant_state
merchant_region
merchant_status
payment_method_id
payment_method_name
payment_method_type
payment_method_brand
```

Exemplo conceitual:

```json
{"transaction_id":123,"transaction_at":"2026-01-05T18:37-03:00","transaction_amount":84.9,"transaction_status":"approved","customer_id":150,"customer_name":"João Silva","customer_email":"joao.silva.0150@example.com","customer_city":"São Paulo","customer_state":"SP","customer_region":"Sudeste","customer_status":"active","merchant_id":37,"merchant_name":"Restaurante Aurora 037","merchant_category":"alimentacao","merchant_city":"São Paulo","merchant_state":"SP","merchant_region":"Sudeste","merchant_status":"active","payment_method_id":1,"payment_method_name":"Pix","payment_method_type":"pix","payment_method_brand":null}
```

## Mundo verdadeiro x fonte imperfeita

A ideia central é: primeiro o código cria customers e merchants estáveis. Uma transação limpa sempre usa dados coerentes dessas entidades. Só depois a linha pronta pode receber um problema de qualidade.

Assim, sujeira não é usada para construir a realidade sintética.

## Problemas de qualidade

Cerca de 3% das transações recebem **no máximo um** destes problemas:

- case ou whitespace em campo textual;
- email em uppercase + whitespace;
- região inconsistente com o estado;
- amount igual a zero ou negativo;
- `transaction_id = null`;
- `customer_id = null`;
- `transaction_status = "unknown"`;
- `payment_method_type` fora do domínio.

Além disso, cerca de 0,2% das transações recebem uma cópia exata como duplicata.

As taxas são probabilísticas, portanto não existe uma quantidade pré-definida. A seed fixa faz com que a execução continue reproduzível.

## Regras principais

### Customers

Status aproximado:

```text
active    92%
inactive   5%
blocked    3%
```

O status não muda ao longo dos 45 dias.

### Merchants

Aproximadamente 97% são `active` e 3% `inactive`.

### Status da transação

Regras obrigatórias antes da sujeira:

```text
customer inactive -> declined
customer blocked  -> declined
merchant inactive -> declined
```

Quando customer e merchant estão ativos, `approved` é muito comum e `declined`, `pending` e `refunded` são menos comuns.

Cartões têm uma pequena taxa de recusa maior que Pix.

### Valores

A categoria determina uma faixa simples. Por exemplo:

```text
transporte      5 .. 80
alimentacao    15 .. 180
supermercado   40 .. 500
eletronicos   200 .. 5000
```

O objetivo é só impedir que todas as categorias tenham exatamente o mesmo perfil financeiro.

### Pagamento

Valores pequenos favorecem Pix/débito. Valores grandes favorecem crédito.

## Alterações mais comuns

Para gerar outro período, mudar quantidades ou taxas, edite `config.py`.

Para mudar categorias, cidades, payment methods ou faixas de valor, edite `data.py`.

Para entender a lógica inteira do gerador, leia `generator.py` de cima para baixo. Ele foi mantido procedural e direto.