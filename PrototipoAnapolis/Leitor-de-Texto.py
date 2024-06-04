from PyPDF2 import PdfReader
import re
import pandas as pd


def processamento_dividas(PDF, CSV):

    try:
        df_csv = pd.read_csv(CSV, encoding='latin1', sep=";")
    except UnicodeDecodeError:
        df_csv = pd.read_csv(CSV, encoding='iso-8859-1')
    
    csv_data = df_csv[["NMLOCAL", "DEOBSERVACAO", "NMEMPRESA", "CDEMPRESAVIEW", "NMEMPREEND", "CDEMPREENDVIEW", "NUUNIDADE", "SITUACAO", "NUCONTRATOVIEW", "NUTITULO", "Nome_Cliente", "CIDADE", "CNPJ", "QTAREAPRIV", "QTAREACOMUM"]]

    # Abrir pedef em Binários.
    with open(PDF, "rb") as file_pdf:
        reader_pdf = PdfReader(file_pdf)
        num_paginas = len(reader_pdf.pages)

        text = ""
        imoveis = []

        # Iterando entre paginas do PDF.
        for num_pagina in range(num_paginas):
            pagina = reader_pdf.pages[num_pagina]
            # Extração do texto das paginas
            text += pagina.extract_text()
            # Debugging de leitura de arquivo.
            print(text)

        # Formatando e eliminando sobras desnecessárias
        text = re.sub(r"\.(\s*\.)+", "\n", text)
        text = re.sub(
            r"ANO MÊS TRIBUTO VL. ATUAL. JUROS MULTA TOTAL VENCIDAS / A VENCER",
            "\n",
            text,
        )
        text = re.sub(r"^.*TOTAL:$", "\n", text, flags=re.MULTILINE)
        text = re.sub(r"^.*ANÁPOLIS$", "\n", text, flags=re.MULTILINE)
        text = re.sub(r"^Página.*$", "\n", text, flags=re.MULTILINE)
        text = re.sub(r"^Data:.*$", "\n", text, flags=re.MULTILINE)
        text = re.sub(r",\s(.+?)Matrícula:\s", "\n", text, flags=re.MULTILINE)
        text = re.sub(r";\s(.+?)Matrícula:\s", "\n", text, flags=re.MULTILINE)
        text = re.sub(r"\d(.+?)Matrícula:\s", "\n", text, flags=re.MULTILINE)
        text = re.sub(r"\n+", "\n", text)
        text = text.strip()
        text = re.sub(r"(Endereço:)", r"\n\n\1", text)
        text = re.sub(r"(Total Dívida Corrente:)", r"\n\n\1", text)

        # Padronizando leitura de textos para extração de variaveis de identificação.
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

            padrao_quadra = re.compile(r"Q[Dd].(.+?)\s")
            padrao_lote = re.compile(r"L[Tt].(.+?)\s")

            correspondencia_quadra = padrao_quadra.findall(endereco)
            correspondencia_lote = padrao_lote.findall(endereco)

            quadra = correspondencia_quadra[0].strip() if correspondencia_quadra else ""
            lote = correspondencia_lote[0].strip() if correspondencia_lote else ""

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

    dfs = []

    # Depuração de resultados.
    for imovel in imoveis:
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
                    "A Vencer",
                ],
            )

            # Adicionando o DataFrame atual à lista
            if any(df["Inscrição"].isin(df_csv["NMLOCAL"])):
                dfs.append(df)
                indices_correspondentes = df[df["Inscrição"].isin(df_csv["NMLOCAL"])].index
                valores_correspondentes = csv_data.loc[df_csv["NMLOCAL"].isin(df["Inscrição"])]
                for coluna in csv_data.columns:
                    df.loc[indices_correspondentes, coluna] = valores_correspondentes[coluna].values


    # Concatenando todos os DataFrames na lista em um único DataFrame
    if dfs:  # Verifica se a lista de DataFrames não está vazia
        df_final = pd.concat(dfs, ignore_index=True)
    else:
        # Se a lista de DataFrames estiver vazia, cria um DataFrame vazio
        df_final = pd.DataFrame()

    return df_final

PDF = "sample.pdf"
CSV = "data.csv"

df_final = processamento_dividas(PDF, CSV)

print(df_final, "1")

total_divida = df_final["Total Divida"].sum()
total_multa = df_final["Multa"].sum()
total_juros = df_final["Juros"].sum()
total_valor_atual = df_final["Valor Atual"].sum()

resultados = {
    "DEOBSERVACAO": "Totais R$:",
    "Inscrição": "",
    "Quadra": "",
    "Lote": "",
    "Origem": "",
    "Tributo": "",
    "Ano": "",
    "Mês": "",
    "Situação": "",
    "Valor Atual": total_valor_atual,
    "Juros": total_juros,
    "Multa": total_multa,
    "Total Divida": total_divida,
    "Vencidas": "",
    "A Vencer": "",
    "NMEMPRESA": "",
    "CDEMPRESAVIEW": "",
    "NMEMPREEND": "",
    "CDEMPREENDVIEW": "",
    "NUUNIDADE": "",
    "SITUACAO": "",
    "NUCONTRATOVIEW": "",
    "NUTITULO": "",
    "Nome_Cliente": "",
    "CIDADE": "",
    "CNPJ": "",
    "QTAREAPRIV": "",
    "QTAREACOMUM": ""
}

# Converte os resultados em um dataframe para concatena-ló ao dataframe df_final.
resultados_df = pd.DataFrame([resultados])
df_final = pd.concat([df_final, resultados_df], ignore_index=True)

coluns = [
    "DEOBSERVACAO", 
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
    "A Vencer", 
    "NMEMPRESA", 
    "CDEMPRESAVIEW", 
    "NMEMPREEND",
    "CDEMPREENDVIEW",
    "NUUNIDADE",
    "SITUACAO",
    "NUCONTRATOVIEW",
    "NUTITULO", 
    "Nome_Cliente", 
    "CIDADE",
    "CNPJ",
    "QTAREAPRIV",
    "QTAREACOMUM"
    ]
df_final = df_final[coluns]

df_final = df_final.rename(columns={
    "DEOBSERVACAO": "Observação",
    "NMEMPRESA": "Empresa",
    "CDEMPRESAVIEW": "Cod. Empresa",
    "NMEMPREEND": "Empreendimento",
    "CDEMPREENDVIEW": "Cod. Empreendimento",
    "NUUNIDADE": "Unidade",
    "SITUACAO": "Disponibilidade",
    "NUCONTRATOVIEW": "Contrato",
    "NUTITULO": "Titulo",
    "Nome_Cliente": "Cliente",
    "CIDADE": "Cidade",
    "QTAREAPRIV": "Área Priv.",
    "QTAREACOMUM": "Área Com."
})

order = [
    "Observação", 
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
    "A Vencer", 
    "Empresa", 
    "Cod. Empresa", 
    "Empreendimento",
    "Cod. Empreendimento",
    "Unidade",
    "Disponibilidade",
    "Contrato",
    "Titulo", 
    "Cliente", 
    "Cidade",
    "CNPJ",
    "Área Priv.",
    "Área Com."
]
df_final = df_final.reindex(columns=order)

df_final = df_final[order]

# Salvando arquivo em .CSV
df_final.to_csv("RelatórioFinal.csv", index=False)
print("Arquivo CSV Salvo com sucesso!")

# Salvando arquivo em formato Excel
Excel = "RelatórioFinal.xlsx"
with pd.ExcelWriter(Excel, engine="xlsxwriter") as writer:
    df_final.to_excel(writer, index=False)
    print("Arquivo Excel Salvo com sucesso!")

    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]  # Define o nome da planilha para Sheet1

    blue_format = workbook.add_format({"bg_color": "#C6E2FF", "align": "left"})
    white_format = workbook.add_format({"bg_color": "#FEFEFE", "align": "left"})
    bold_format = workbook.add_format({"bold": True, "bg_color": "#666666", "color": "#ffffff", "align": "left"})

    for row_num in range(1, len(df_final) + 1):
        if row_num % 2 == 0:
            worksheet.set_row(row_num, cell_format=blue_format)
        else:
            worksheet.set_row(row_num, cell_format=white_format)

        if df_final.iloc[row_num - 1]["Inscrição"] == "R$:":
            worksheet.set_row(row_num, cell_format=bold_format)

    worksheet.set_column("A:A", 64+8)  # Define a largura da coluna "A"
    worksheet.set_column("B:B", 16)
    worksheet.set_column("F:F", 16)
    worksheet.set_column("I:I", 14)
    worksheet.set_column("F:G", 6)
    worksheet.set_column("J:J", 10)
    worksheet.set_column("M:M", 10)
    worksheet.set_column("P:P", 28)
    worksheet.set_column("Q:Q", 12)
    worksheet.set_column("R:R", 28)
    worksheet.set_column("S:S", 20)
    worksheet.set_column("T:T", 12)
    worksheet.set_column("U:V", 18)
    worksheet.set_column("X:X", 28)
    worksheet.set_column("Y:Y", 10)
    worksheet.set_column("Z:Z", 12)
