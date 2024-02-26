from PyPDF2 import PdfReader
import re
import pandas as pd

def processamento_dividas(PDF):
    # Abrir pedef em Binários.
    with open(PDF, "rb") as file_pdf:
        reader_pdf = PdfReader(file_pdf)
        num_paginas = len(reader_pdf.pages)

        text = ""
        imoveis = []
        iss = []

        # Iterando entre paginas do PDF.
        for num_pagina in range(num_paginas):
            pagina = reader_pdf.pages[num_pagina]
            # Extração do texto das paginas
            text += pagina.extract_text()
            # Debugging de leitura de arquivo.
            print(text)

        text = re.sub(r"\.(\s*\.)+", "\n", text)
        text = re.sub(
            r"ANO MÊS TRIBUTO VL. ATUAL. JUROS MULTA TOTAL VENCIDAS / A VENCER",
            "\n",
            text,
        )
        text = re.sub(r"^.*TOTAL:$", "\n", text, flags=re.MULTILINE)
        # text = re.sub(r'^TOTAL ORIGEM:.*$', '\n', text, flags=re.MULTILINE)
        text = re.sub(r"^.*ANÁPOLIS$", "\n", text, flags=re.MULTILINE)
        text = re.sub(r"^Página.*$", "\n", text, flags=re.MULTILINE)
        text = re.sub(r"^Data:.*$", "\n", text, flags=re.MULTILINE)
        # text = re.sub(r'Total Dívida Corrente:.*?OBSERVAÇÃO:.*', '\n\n\1', text, flags=re.DOTALL)
        text = re.sub(r",\s(.+?)Matrícula:\s", "\n", text, flags=re.MULTILINE)
        text = re.sub(r";\s(.+?)Matrícula:\s", "\n", text, flags=re.MULTILINE)
        text = re.sub(r"\d(.+?)Matrícula:\s", "\n", text, flags=re.MULTILINE)
        text = re.sub(r"\n+", "\n", text)
        text = text.strip()
        text = re.sub(r"(Endereço:)", r"\n\n\1", text)
        text = re.sub(r"(Total Dívida Corrente:)", r"\n\n\1", text)

        # print(text)

        padrao_origem = re.compile(r"Inscrição:\s(.+?)\sOrigem:")
        padrao_inscricao = re.compile(r"\n(.+?)\s*Inscrição:")
        padrao_endereco = re.compile(r"Endereço:\s*(.+?)\n")
        padrao_data = re.compile(r"Origem:(.+?)\n\n", re.DOTALL)

        # Correspondencia de Headers.
        correspondencia_origem = padrao_origem.findall(text)
        correspondencia_inscricao = padrao_inscricao.findall(text)
        correspondencia_endereco = padrao_endereco.findall(text)
        correspondencia_data = padrao_data.findall(text)

        for origem, endereco, inscricao, data in zip(
            correspondencia_origem,
            correspondencia_endereco,
            correspondencia_inscricao,
            correspondencia_data,
        ):
            # origem = origem.strip()
            # endereco = endereco.strip()
            # inscricao = inscricao.strip()

            padrao_quadra = re.compile(r"Q[Dd].(.+?)\s")
            padrao_lote = re.compile(r"L[Tt].(.+?)\s")

            correspondencia_quadra = padrao_quadra.findall(endereco)
            correspondencia_lote = padrao_lote.findall(endereco)

            quadra = (
                correspondencia_quadra[0].strip() if correspondencia_quadra else ""
            )
            lote = correspondencia_lote[0].strip() if correspondencia_lote else ""

            # print(quadra, lote)

            data = re.sub(r"(Dívida)", r"\n\n\1", data)
            data = re.sub(r"(Ajuizada)", r"\n\n\1", data)
            data = re.sub(r"^TOTAL ORIGEM:.*$", "\n", data, flags=re.MULTILINE)

            padrao_dividas = re.compile(r"\n(.+?)\n\n", re.DOTALL)
            correspondencia_dividas = padrao_dividas.findall(data)

            dividas = []
            total_origem = 0

            if correspondencia_dividas:
                for dividas_cliente in correspondencia_dividas:

                    padrao_situacao = re.compile(r"\n*(.+?)Situação:")
                    correspondencia_situacao = padrao_situacao.findall(dividas_cliente)
                    situacao = (
                        correspondencia_situacao[0].strip()
                        if correspondencia_situacao
                        else "Desconhecida"
                    )

                    divida = []
                    total_dividas = 0

                    for linha in dividas_cliente.strip().split("\n"):
                        padrao_linha = re.compile(
                            r"(\d{4}) (\d{2}) (.*?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d+) (\d+)"
                        )
                        correspondencia_linha = padrao_linha.match(linha)

                        if correspondencia_linha:
                            (
                                ano,
                                mes,
                                tributo,
                                valor_atual,
                                juros,
                                multa,
                                total,
                                vencidas,
                                a_vencer,
                            ) = correspondencia_linha.groups()
                            valor_atual = valor_atual.replace(".", "").replace(",", ".")
                            juros = juros.replace(".", "").replace(",", ".")
                            multa = multa.replace(".", "").replace(",", ".")
                            total = total.replace(".", "").replace(",", ".")
                            ano, mes, tributo = map(str, [ano, mes, tributo])
                            valor_atual, juros, multa, total = map(
                                float, [valor_atual, juros, multa, total]
                            )
                            vencidas, a_vencer = map(int, [vencidas, a_vencer])
                            total_dividas += float(total)
                            divida.append(
                                {
                                    "Inscrição": inscricao,
                                    "Quadra": quadra,
                                    "Lote": lote,
                                    "Origem": origem,
                                    "Ano": ano,
                                    "Mês": mes,
                                    "Tributo": tributo,
                                    "Situação": situacao,
                                    "Valor Atual": valor_atual,
                                    "Juros": juros,
                                    "Multa": multa,
                                    "Total Divida": total,
                                    "Vencidas": vencidas,
                                    "A Vencer": a_vencer,
                                }
                            )

                    total_origem += float(total_dividas)
                    dividas.append({"Divida": divida, "Total Origem": total_origem})

            imoveis.append({"Inscrição": inscricao, "Dívidas": dividas})

    return imoveis


PDF = "sample.pdf"
imoveis_resultados = processamento_dividas(PDF)

# Depuração de resultados.
dfs = []

# Depuração de resultados.
for i, imovel in enumerate(imoveis_resultados, start=1):
    inscricao = imovel["Inscrição"]
    dividas = imovel["Dívidas"]

    for divida in dividas:
        df = pd.DataFrame(
            divida["Divida"],
            columns=[
                "Inscrição",
                "Quadra",
                "Lote",
                "Origem",
                "Tributo",
                "Ano",
                "Mês",
                "Situação",
                "Valor Atual",
                "Juros",
                "Multa",
                "Total Divida",
                "Vencidas",
                "A Vencer"
            ],
        )

        # Adicionando o DataFrame atual à lista
        dfs.append(df)

# Concatenando todos os DataFrames na lista em um único DataFrame
df_final = pd.concat(dfs, ignore_index=True)

print(df_final)

# Ler o arquivo CSV
df_csv = pd.read_csv("data.csv", delimiter=";")

# Iterar sobre as linhas do DataFrame do arquivo CSV
if isinstance(df_final, pd.DataFrame) and isinstance(df_csv, pd.DataFrame):
    # Iterar sobre as linhas do DataFrame do arquivo CSV
    for index, row in df_csv.iterrows():
        # Encontrar índices onde a Inscrição do df_final corresponde à INSCRICAO_IMOBILIARIA do df_csv
        matching_indices = df_final[df_final["Inscrição"] == row['INSCRICAO_IMOBILIARIA']].index
        
        # Iterar sobre os índices encontrados
        for idx in matching_indices:
            # Adicionar os dados ausentes ao DataFrame existente
            df_final.at[idx, 'Contribuinte'] = row['CONTRIBUINTE']
            # df_final.at[idx, 'ENDERECO'] = row['ENDERECO']
            # df_final.at[idx, 'QUADRA'] = row['QUADRA']
            # df_final.at[idx, 'LOTE'] = row['LOTE']
            df_final.at[idx, 'Área Lt'] = row['AREA_LOTE']
            df_final.at[idx, 'Área Un'] = row['AREA_UNIDADE']
            df_final.at[idx, 'TESTADA_M'] = row['TESTADA_M']
            df_final.at[idx, 'Oupação'] = row['OCUPACAO']
            df_final.at[idx, 'Status Imóvel'] = row['SITUACAO']
else:
    print("df_final e df_csv devem ser DataFrames do pandas.")
        
total_divida = df_final["Total Divida"].sum()
total_multa = df_final["Multa"].sum()
total_juros = df_final["Juros"].sum()
total_valor_atual = df_final["Valor Atual"].sum()

resultados = {
    "Inscrição": "R$:",
    "Quadra": "",
    "Lote": "",
    "Origem": "",
    "Tributo": "",
    "Ano": "",
    "Mês": "JUROS:",
    "Situação": total_juros,
    "Valor Atual": "      MULTA:",
    "Juros": total_multa,
    "Multa": "      GERAL:",
    "Total Divida": total_divida,
    "Vencidas": "",
    "A Vencer": "",
    "Área Lt": "",
    "Área Un": "",
    "TESTADA_M": "",
    "Oupação": "",
    "Status Imóvel": ""
}

df_total = pd.DataFrame([resultados])

df_exel = pd.concat([df_final, df_total], ignore_index=True)

# Depuração do DataFrame final
print(df_exel)

# Salvando arquivo .CSV
df_exel.to_csv("RelatórioFinal.csv", index=False)
print("Arquivo CSV Salvo com sucesso!")

# Salvando arquivo em formato Excel
Excel = "RelatórioFinal.xlsx"
with pd.ExcelWriter(Excel, engine="xlsxwriter") as writer:
    df_exel.to_excel(writer, index=False)
    print("Arquivo Exel Salvo com sucesso!")
    
    workbook = writer.book
    worksheet = writer.sheets[
        "Sheet1"
    ]  # Mude 'Sheet1' para o nome da sua planilha, se necessário

    blue_format = workbook.add_format({"bg_color": "#C6E2FF"})
    white_format = workbook.add_format({"bg_color": "#FEFEFE"})

    bold_format = workbook.add_format({"bold": True})

    for row_num in range(1, len(df_final) + 1):
        if row_num % 2 == 0:
            worksheet.set_row(row_num, cell_format=blue_format)
        else:
            worksheet.set_row(row_num, cell_format=white_format)

        if df_exel.iloc[row_num - 1]["Inscrição"] == "R$:":
            worksheet.set_row(row_num, cell_format=bold_format)

    worksheet.set_column("A:A", 16)  # Define a largura da coluna 'A' para 15
    worksheet.set_column("B:C", 6)
    worksheet.set_column("D:D", 12)
    worksheet.set_column("E:E", 14)
    worksheet.set_column("F:G", 6)
    worksheet.set_column("H:H", 14)
    worksheet.set_column("I:L", 12)
    worksheet.set_column("M:N", 8)
    worksheet.set_column("O:O", 28)
    worksheet.set_column("T:T", 12)