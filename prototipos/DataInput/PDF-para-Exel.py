import tabula
import pandas as pd

# Define o nome do arquivo PDF
file = "sample.pdf"

# Extrair tabelas do PDF
tabelas = tabula.read_pdf(file, pages='all', multiple_tables=True, stream=True, guess=False)

# Inicializar um DataFrame vazio
df_final = pd.DataFrame()

# Concatenar todas as tabelas em um único DataFrame
for tabela in tabelas:
    df_final = pd.concat([df_final, tabela], ignore_index=True)

# Define o caminho completo do arquivo Excel
excel = "resultados.xlsx"

# Salvar o DataFrame em um arquivo Excel
df_final.to_excel(excel, index=False)

print(f'Conversão concluída. Dados salvos em {excel}')