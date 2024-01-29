# Exemplo de estrutura de dados (substitua isso pelos seus dados reais)
dividas = [
    {"cliente": "Alice", "tipo": "alimentacao", "valor": 100},
    {"cliente": "Bob", "tipo": "transporte", "valor": 150},
    {"cliente": "Alice", "tipo": "transporte", "valor": 200},
    {"cliente": "Bob", "tipo": "alimentacao", "valor": 50},
]

# Somar todas as dívidas de transporte de todos os clientes
soma_transportes = 0

# Dicionário para armazenar as somas individuais de dívidas por cliente
somas_por_cliente = {}

for divida in dividas:
    cliente = divida["cliente"]
    tipo = divida["tipo"]
    valor = divida["valor"]

    # Somar todas as dívidas de transporte de todos os clientes
    if tipo == "transporte":
        soma_transportes += valor

    # Somar todas as dívidas de um cliente, seja de transporte ou alimentação
    if cliente in somas_por_cliente:
        somas_por_cliente[cliente] += valor
    else:
        somas_por_cliente[cliente] = valor

print(f"Soma de todas as dívidas de transporte: {soma_transportes}")

print("\nSomas de dívidas por cliente:")
for cliente, soma in somas_por_cliente.items():
    print(f"{cliente}: {soma}")
