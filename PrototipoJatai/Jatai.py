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

        # Iterando entre paginas do PDF.
        for num_pagina in range(num_paginas):
            pagina = reader_pdf.pages[num_pagina]
            # Extração do texto das paginas
            text = pagina.extract_text()  # Limpa o texto anterior
            # Debugging de leitura de arquivo.
            # print(text)

            text = re.sub(r"\s\d\sPágina.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(r"\s\d\d\sPágina.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(r"^\s\sImpresso.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(r"^Débito.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(r"^Ramo.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(r"^Endereço:.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(
                r"PREFEITURA\sMUNICIPAL\sDE\sJATAÍ", "\n", text, flags=re.MULTILINE
            )
            text = re.sub(
                r"MUNICÍPIO\sDE\sJATAÍ\s-\sESTADO\sDE\sGOIÁS",
                "\n",
                text,
                flags=re.MULTILINE,
            )
            text = re.sub(r"Rua\sItarumã,.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(r",\sCIDADE:(.+?)\nPE", "\nPE", text, flags=re.MULTILINE)
            text = re.sub(r",\sJATAÍ:(.+?)\nPE", "\nPE", text, flags=re.MULTILINE)
            text = re.sub(
                r"\b(TX)\s+(EXP)\s+(ALV)\b", r"\1\2\3", text, flags=re.MULTILINE
            )
            text = re.sub(r"\b(ISS)\s+(RET)\b", r"\1\2", text, flags=re.MULTILINE)
            text = re.sub(r"^Inicio\sAtividade:.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(r"^CORRETAGEM.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(r"QD\.\:", "QD.", text, flags=re.MULTILINE)
            text = re.sub(r"LT\.\:", "LT.", text, flags=re.MULTILINE)
            text = re.sub(r"ADC:(.+?)\n\n", "\n", text, flags=re.DOTALL)
            text = re.sub(r"\n+", "\n", text)
            text = re.sub(
                r"EXTRATO\sDE\sDÉBITO", "\nEXTRATO DE DÉBITO", text, flags=re.MULTILINE
            )
            print("Texto formatado:\n", text)

            padrao_data = re.compile(r"EXTRATO DE DÉBITO(.+?)(?=EXTRATO DE DÉBITO|$)", re.DOTALL)
            correspondencia_data = padrao_data


            ocorrencias_dividas = correspondencia_data.findall(text)

            # i = 0
            for ocorrencia_divida in ocorrencias_dividas:
                # i += 1
                # print(f"\n{i} - Dívida encontrada.")

                dividas = []
                total_origem = 0

                # padrao_inscricao_cci = re.compile(r"Inscrição:\s(\d+)CCI", re.DOTALL)
                # correspondencia_incricao_cci = padrao_inscricao_cci.search(ocorrencia_divida)

                # if correspondencia_incricao_cci:
                #     inscricao_cci = correspondencia_incricao_cci.group(1)
                #     print("Número de inscrição CCI:", inscricao_cci)
                # else:
                #     inscricao_cci = None
                #     print("Número de inscrição CCI não encontrado.")

                padrao_local = re.compile(r"\n(.+?),", re.DOTALL)
                correspondencia_local = padrao_local.search(ocorrencia_divida)

                if correspondencia_local:
                    local = correspondencia_local.group(1)
                    # print("Local:", local)
                else:
                    local = None
                    # print("Local não encontrado.")

                padrao_quadra = re.compile(r"QD.(.+?),", re.DOTALL)
                correspondencia_quadra = padrao_quadra.search(ocorrencia_divida)

                if correspondencia_quadra:
                    quadra = correspondencia_quadra.group(1)
                    # print("Número da quadra:", quadra)
                else:
                    quadra = None
                    # print("Número da quadra não encontrado.")

                padrao_lote = re.compile(r"LT.(.+?),", re.DOTALL)
                correspondencia_lote = padrao_lote.search(ocorrencia_divida)

                if correspondencia_lote:
                    lote = correspondencia_lote.group(1)
                    # print("Número do lote:", lote)
                else:
                    lote = None
                    # print("Número do lote não encontrado.")

                padrao_bairro = re.compile(r"BAIRRO:\s(.+?),", re.DOTALL)
                correspondencia_bairro = padrao_bairro.search(ocorrencia_divida)

                if correspondencia_bairro:
                    bairro = correspondencia_bairro.group(1)
                    # print("Bairro:", bairro)
                else:
                    bairro = None
                    # print("Bairro não encontrado.")

                padrao_cidade = re.compile(r"CIDADE:\s(.+?),", re.DOTALL)
                correspondencia_cidade = padrao_cidade.search(ocorrencia_divida)

                if correspondencia_cidade:
                    cidade = correspondencia_cidade.group(1)
                    # print("Cidade:", cidade)
                else:
                    cidade = None
                    # print("Cidade não encontrada.")

                data_dividas = re.findall(
                    r"PE.*?\w\s-\s\d+", ocorrencia_divida, re.DOTALL
                )
                # data_dividas = '\n'.join(data_dividas)

                for linha in data_dividas:
                    total_dividas = 0

                    padrao_cod = re.findall(r"\w\s-\s\d+", linha, re.DOTALL)
                    correspondencia_cod = padrao_cod[0] if padrao_cod else None
                    inscricao = correspondencia_cod
                    # Dividir a linha pelos espaços em branco
                    valores = linha.split()

                    status = valores[0]
                    parcela = valores[1]
                    porcentagem = valores[2]
                    variavel4 = valores[3]
                    multa = valores[4]
                    variavel6 = valores[5]
                    total = valores[6]
                    valor_tributo = valores[7]
                    variavel9 = valores[8]
                    vencimento = valores[9]
                    tributo = valores[10]
                    base = valores[11]
                    correcao = valores[12]
                    juros = valores[13]
                    debito = valores[14]
                    ref = valores[15]
                    desconto = valores[16]

                    valor_tributo = valor_tributo.replace(".", "").replace(",", ".")
                    base = base.replace(".", "").replace(",", ".")
                    juros = juros.replace(".", "").replace(",", ".")
                    multa = multa.replace(".", "").replace(",", ".")
                    total = total.replace(".", "").replace(",", ".")
                    correcao = correcao.replace(".", "").replace(",", ".")

                    valor_tributo, base, juros, multa, total, correcao, desconto = map(
                        float,
                        [valor_tributo, base, juros, multa, total, correcao, desconto],
                    )

                    inscricao = re.sub(r"[A-Za-z\s-]", "", inscricao)

                    # Exibir os valores
                    # print(
                    #     f"\nVariáveis: Débito: {debito}, Tributo: {tributo}, Status: {status}, Ref.: {ref}, Parcela: {parcela}, Base: {base}, Porcentagem: {porcentagem}, Juros: {juros}, Multa: {multa}, Correção: {correcao}, Valor Tributo: {valor_tributo}, Desconto: {desconto}, Total: {total}, Vencimento: {vencimento}"
                    # )
                    # print(
                    #     f"Variáveis não identificadas: {variavel4}, {variavel6}, {variavel9}"
                    # )

                    total_dividas += float(total)
                    divida = {
                        "Inscrição": inscricao,
                        "Local": local,
                        "Quadra": quadra,
                        "Lote": lote,
                        "Status": status,
                        "Parcela": parcela,
                        "Porcentagem": porcentagem,
                        "Multa": multa,
                        "Valor Tributo": valor_tributo,
                        "Vencimento": vencimento,
                        "Tributo": tributo,
                        "Base": base,
                        "Correção": correcao,
                        "Juros": juros,
                        "Débito": debito,
                        "Ref": ref,
                        "Desconto": desconto,
                        "Total Divida": total,
                    }
                    dividas.append(divida)

                total_origem += float(total_dividas)
                imovel = {
                    "Dividas": dividas,
                    # "Inscrição": inscricao,
                    "Total Origem": total_origem,
                }
                imoveis.append(imovel)

    return imoveis


PDF = "sample.pdf"
imoveis_resultados = processamento_dividas(PDF)
# print(imoveis_resultados)
dfs = []

for i, imovel in enumerate(imoveis_resultados, start=1):
    # inscricao_cci = imovel["Inscrição"]
    dividas = imovel["Dividas"]

    for divida in dividas:
        df = pd.DataFrame(
            [divida],
            columns=[
                "Inscrição",
                # "Local",
                "Quadra",
                "Lote",
                "Status",
                "Tributo",
                "Ref",
                "Base",
                "Valor Tributo",
                "Parcela",
                "Porcentagem",
                "Juros",
                "Multa",
                "Correção",
                "Desconto",
                "Total Divida",
                "Vencimento",
                # "Débito"
            ],
        )

        dfs.append(df)

df_final = pd.concat(dfs, ignore_index=True)

total_tributos = df_final["Valor Tributo"].sum()
total_juros = df_final["Juros"].sum()
total_multas = df_final["Multa"].sum()
total_correcao = df_final["Correção"].sum()
total_descontos = df_final["Desconto"].sum()
total_dividas = df_final["Total Divida"].sum()
total_base = df_final["Base"].sum()

resultados = {
    "Inscrição": "R$:",
    # "Local",
    "Quadra": "Totais",
    "Lote": "",
    "Status": "",
    "Tributo": "",
    "Ref": "",
    "Base": total_base,
    "Valor Tributo": total_tributos,
    "Parcela": "",
    "Porcentagem": "",
    "Juros" : total_juros,
    "Multa": total_multas,
    "Correção": total_correcao,
    "Desconto": total_descontos,
    "Total Divida": total_dividas,
    "Vencimento": "",
    # "Débito"
}

df_total = pd.DataFrame([resultados])

df_exel = pd.concat([df_final, df_total], ignore_index=True)

print(f"\nDataFrame:\n{df_exel}")

df_exel.to_csv("RelatórioFinal.csv", index=False)
print("Arquivo CSV Salvo com sucesso!")

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
    bold_format = workbook.add_format({"bold": True, "bg_color": "#666666", "color": "#ffffff"})

    for row_num in range(1, len(df_exel) + 1):
        if row_num % 2 == 0:
            worksheet.set_row(row_num, cell_format=blue_format)
        else:
            worksheet.set_row(row_num, cell_format=white_format)

        if df_exel.iloc[row_num - 1]["Inscrição"] == "R$:":
            worksheet.set_row(row_num, cell_format=bold_format)

    worksheet.set_column("A:A", 10)
    worksheet.set_column("B:D", 6)
    worksheet.set_column("E:H", 12)
    worksheet.set_column("I:I", 8)
    worksheet.set_column("J:J", 12)
    worksheet.set_column("K:O", 10)
    worksheet.set_column("P:P", 12)
