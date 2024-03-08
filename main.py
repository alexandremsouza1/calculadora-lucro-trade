"""
    NOTA:
        o programa remove linhas que não possuem dados necessários.
        Isso pode acarretar em um resultado final inexato - quanto mais linhas removidas,
        maior a diferença entre o valor real.
        Por isso, recomenda-se preencher os dados faltantes.
"""
import pandas as pd
import os
import tempfile
import glob


# Obtém o caminho do diretório atual do script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Checa se o arquivo movimentacao.xlsx existe
if not os.path.exists(os.path.join(script_dir, "files", "movimentacao.xlsx")):
    print("Arquivo movimentacao.xlsx não encontrado.")
    exit()

EXCEL_PATH = os.path.join(script_dir, "files", "movimentacao.xlsx")

# Altera o diretório de trabalho para o diretório temporário
os.chdir(tempfile.gettempdir())

# Carrega os dados do Excel
data = pd.read_excel(EXCEL_PATH)

# Remove linhas que não possuem valor na coluna "Valor da Operação" ou "Quantidade"
data["Valor da Operação"] = pd.to_numeric(data["Valor da Operação"], errors='coerce')
data['Quantidade'] = pd.to_numeric(data["Quantidade"], errors='coerce')
data = data.dropna()

# Cria nova coluna 'ticket'
data.Produto.str.strip()
data[["ticket", "trash"]] = data.Produto.str.split(' ', n=1, expand=True)
data = data.drop(columns='trash')

# Ordena por data
data["Data"] = pd.to_datetime(data["Data"], format="%d/%m/%Y", dayfirst=True)
data = data.sort_values(by=["Data"])

# Obtem ativos operados
tickets = data["ticket"]
tickets = tickets.to_list()
tickets = list(set(tickets))

lucro_total = 0
for ticket in tickets:
    stock_data = data.loc[data['ticket'] == ticket]

    lucro = 0
    qtd_acao_comprada = 0
    qtd_acao_vendida = 0
    valor_total_compra = 0
    valor_total_venda = 0

    for index, row in stock_data.iterrows():
        if row["Entrada/Saída"] == "Credito":
            qtd_acao_comprada += row["Quantidade"]
            valor_total_compra += row["Valor da Operação"]
        elif row["Entrada/Saída"] == "Debito":
            qtd_acao_vendida += row["Quantidade"]
            valor_total_venda += row["Valor da Operação"]
        else:
            continue

    if qtd_acao_vendida > 0 and qtd_acao_comprada > 0:
        # calcula o preço médio de venda e de compra,
        pm_compra = valor_total_compra / qtd_acao_comprada
        pm_venda = valor_total_venda / qtd_acao_vendida

        # obtem a qtd operada de ações        
        qtd_calculo = min(qtd_acao_comprada, qtd_acao_vendida)

        # calcula o valor de compra e de venda
        credito = qtd_calculo * pm_compra
        debito = qtd_calculo * pm_venda        

        lucro = debito - credito

        print(f"{ticket}: {lucro}")
        lucro_total += lucro

first_date = str(data['Data'].iloc[0]).split(" ")[0]
last_date = str(data['Data'].iloc[-1]).split(" ")[0]
from_to = f"{first_date} a {last_date}"
print(f"Lucro total obtido no período ({from_to}): {lucro_total:.2f}")
