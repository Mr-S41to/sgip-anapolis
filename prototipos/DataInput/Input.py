import tabula
import pandas as pd
import os

# Define o nome do arquivo PDF
file_name = "data.pdf"

# Obtém o diretório do script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Define o caminho completo do arquivo PDF
file_path = os.path.join(script_directory, file_name)

# Verifica se o arquivo PDF existe
if not os.path.exists(file_path):
    print(f"Erro: O arquivo PDF '{file_name}' não foi encontrado no diretório '{script_directory}'.")
    exit()

# Extrair tabelas do PDF
tabelas = tabula.read_pdf(file_path, pages='all', multiple_tables=True, stream=True, guess=False)

# Inicializar um DataFrame vazio
df_final = pd.DataFrame()

# Concatenar todas as tabelas em um único DataFrame
for tabela in tabelas:
    df_final = pd.concat([df_final, tabela], ignore_index=True)

# Define o caminho completo do arquivo Excel
excel_path = os.path.join(script_directory, "resultados.xlsx")

# Salvar o DataFrame em um arquivo Excel
df_final.to_excel(excel_path, index=False)

print(f'Conversão concluída. Dados salvos em {excel_path}')
