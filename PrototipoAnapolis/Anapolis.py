from PyPDF2 import PdfReader
import pandas as pd
import zipfile
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import re
import os
import random
import string

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def processamento_dividas(pdf_path, CSV):

    encodings = ["utf-8", "latin-1", "cp1252"]
    df_csv = None
    for encoding in encodings:
        try:
            df_csv = pd.read_csv(CSV, sep=",", encoding=encoding)
            break
        except UnicodeDecodeError as e:
             print(f"Failed to read CSV with encoding {encoding}: {e}")
    csv_data = df_csv[["NMINSCRICAOIMOBILIARIA", "DEOBSERVACAO", "NMEMPRESA", "CDEMPRESAVIEW", "NMEMPREEND", "CDEMPREENDVIEW", "NUUNIDADE", "SITUACAO", "NUCONTRATOVIEW", "NUTITULO", "NMCLIENTE",  "CIDADE", "QTAREAPRIV", "QTAREACOMUM", "CPF_CNPJ"]]

    # Abrir pedef em Binários.
    with open(pdf_path, "rb") as file_pdf:
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
                                    "Endereço": endereco,
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
    df_iss = []
    df_dividas_nao_identificadas = []

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
                    "Endereço"
                ],
            )

            # Adicionando o DataFrame atual à lista
            if any(df["Inscrição"].isin(df_csv["NMINSCRICAOIMOBILIARIA"])):
                dfs.append(df)
                indices_correspondentes = df[df["Inscrição"].isin(df_csv["NMINSCRICAOIMOBILIARIA"])].index
                valores_correspondentes = csv_data.loc[df_csv["NMINSCRICAOIMOBILIARIA"].isin(df["Inscrição"])]
                
                for indexs in indices_correspondentes:
                    for coluna in csv_data.columns:
                        df.at[indexs, coluna] = valores_correspondentes[coluna].values[0]
            
            if all(~df["Inscrição"].isin(df_csv["NMINSCRICAOIMOBILIARIA"])) and any(df["Origem"] != "Inscrição ISS"):
                df_dividas_nao_identificadas.append(df)
                
            if any(df["Origem"] == "Inscrição ISS"):
                df_iss.append(df) 
                
    if not dfs:
        df_final = pd.DataFrame([{
            "Inscrição": "-", 
            "Quadra": "-", 
            "Lote": "-", 
            "Origem": "-", 
            "Tributo": "-", 
            "Ano": "-", 
            "Mês": "-", 
            "Situação": "-", 
            "Valor Atual": "-", 
            "Juros": "-", 
            "Multa": "-", 
            "Total Divida": "-", 
            "Vencidas": "-", 
            "A Vencer": "-", 
            "Endereço": "-"
        }])
        
        resultados = {
            "Inscrição": "Totais R$:",
            "Quadra" : "-",
            "Lote" : "-",
            "Origem" : "-",
            "Tributo" : "-", 
            "Ano" : "-",
            "Mês" : "-",
            "Situação" : "-",
            "Valor Atual" : "-", 
            "Juros"  : "-",
            "Multa" : "-", 
            "Total Divida" : "-", 
            "Vencidas" : "-", 
            "A Vencer" : "-",
            "Endereço": "-"
        }
        resultados_df = pd.DataFrame([resultados])
        df_final = pd.concat([df_final, resultados_df], ignore_index=True)  
    else:
        df_final = pd.concat(dfs, ignore_index=True)
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
            "NMCLIENTE", 
            "CIDADE",
            "CPF_CNPJ",
            "QTAREAPRIV",
            "QTAREACOMUM",
            "Endereço"
        ]
        df_final = df_final[coluns]

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
            "Área Priv.",
            "Área Com.",
            "Endereço"
        ]
        df_final = df_final.reindex(columns=order)
        df_final = df_final[order]
        
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
            "NMCLIENTE": "Cliente",
            "CIDADE": "Cidade",
            "QTAREAPRIV": "Área Priv.",
            "QTAREACOMUM": "Área Com.",
        })
        
        total_divida = df_final["Total Divida"].sum()
        total_multa = df_final["Multa"].sum()
        total_juros = df_final["Juros"].sum()
        total_valor_atual = df_final["Valor Atual"].sum()
        
        resultados = {
            "Observação" : "", 
            "Inscrição": "Totais R$:",
            "Quadra" : "",
            "Lote" : "",
            "Origem" : "",
            "Tributo" : "", 
            "Ano" : "",
            "Mês" : "",
            "Situação" : "",
            "Valor Atual" : total_valor_atual, 
            "Juros"  : total_juros,
            "Multa" : total_multa, 
            "Total Divida" : total_divida, 
            "Vencidas" : "", 
            "A Vencer" : "", 
            "Empresa" : "", 
            "Cod. Empresa" : "",
            "Empreendimento" : "",
            "Cod. Empreendimento" : "",
            "Unidade" : "",
            "Disponibilidade" : "",
            "Contrato" : "",
            "Titulo" : "", 
            "Cliente" : "",
            "Cidade" : "",
            "Área Priv." : "",
            "Área Com." : "",
            "Endereço": ""
        }
        resultados_df = pd.DataFrame([resultados])
        df_final = pd.concat([df_final, resultados_df], ignore_index=True)    
       
    if not df_iss:
        df_iss = pd.DataFrame([{
            "Inscrição": "-", 
            "Quadra": "-", 
            "Lote": "-", 
            "Origem": "-", 
            "Tributo": "-", 
            "Ano": "-", 
            "Mês": "-", 
            "Situação": "-", 
            "Valor Atual": "-", 
            "Juros": "-", 
            "Multa": "-", 
            "Total Divida": "-", 
            "Vencidas": "-", 
            "A Vencer": "-", 
            "Endereço": "-"
        }])
        
        resultados_iss = {
            "Inscrição": "Totais R$:", 
            "Quadra": "-", 
            "Lote": "-", 
            "Origem": "-", 
            "Tributo": "-", 
            "Ano": "-", 
            "Mês": "-", 
            "Situação": "-", 
            "Valor Atual": "-", 
            "Juros": "-", 
            "Multa": "-", 
            "Total Divida": "-", 
            "Vencidas": "-", 
            "A Vencer": "-", 
            "Endereço": "-"
        }
        resultados_iss_df = pd.DataFrame([resultados_iss])
        df_iss = pd.concat([df_iss, resultados_iss_df], ignore_index=True)
    else:
        df_iss = pd.concat(df_iss, ignore_index=True)

        total_divida_iss = df_iss["Total Divida"].sum()
        total_multa_iss = df_iss["Multa"].sum()
        total_juros_iss = df_iss["Juros"].sum()
        total_valor_iss = df_iss["Valor Atual"].sum()
        
        resultados_iss = {
            "Inscrição": "Totais R$:",
            "Origem": "-",
            "Quadra" : "-",
            "Lote": "-",
            "Tributo": "-",
            "Ano": "-",
            "Mês": "-",
            "Situação": "-",
            "Valor Atual": total_valor_iss,
            "Juros": total_juros_iss,
            "Multa": total_multa_iss,
            "Total Divida": total_divida_iss,
            "Vencidas": "-",
            "A Vencer": "-",
            "Endereço": "-"
        }
        resultados_iss_df = pd.DataFrame([resultados_iss])
        df_iss = pd.concat([df_iss, resultados_iss_df], ignore_index=True)
    
    if not df_dividas_nao_identificadas:
        df_dividas_nao_identificadas = pd.DataFrame([{
            "Inscrição": "-", 
            "Quadra": "-", 
            "Lote": "-", 
            "Origem": "-", 
            "Tributo": "-", 
            "Ano": "-", 
            "Mês": "-", 
            "Situação": "-", 
            "Valor Atual": "-", 
            "Juros": "-", 
            "Multa": "-", 
            "Total Divida": "-", 
            "Vencidas": "-", 
            "A Vencer": "-", 
            "Endereço": "-"
        }])
        
        resultados_dividas_nao_identificadas = {
            "Inscrição": "Totais R$:", 
            "Quadra": "-", 
            "Lote": "-", 
            "Origem": "-", 
            "Tributo": "-", 
            "Ano": "-", 
            "Mês": "-", 
            "Situação": "-", 
            "Valor Atual": "-", 
            "Juros": "-", 
            "Multa": "-", 
            "Total Divida": "-", 
            "Vencidas": "-", 
            "A Vencer": "-", 
            "Endereço": "-"
        }
        resultados_dividas_nao_identificadas = pd.DataFrame([resultados_dividas_nao_identificadas])
        df_dividas_nao_identificadas = pd.concat([df_dividas_nao_identificadas, resultados_dividas_nao_identificadas], ignore_index=True)
    else:
        df_dividas_nao_identificadas = pd.concat(df_dividas_nao_identificadas, ignore_index=True)

        total_divida_deconhecida = df_dividas_nao_identificadas["Total Divida"].sum()
        total_multa_desconhecida = df_dividas_nao_identificadas["Multa"].sum()
        total_juros_desconhecida = df_dividas_nao_identificadas["Juros"].sum()
        total_valor_desconhecida = df_dividas_nao_identificadas["Valor Atual"].sum()
        
        resultados_dividas_nao_identificadas = {
            "Inscrição": "Totais R$:",
            "Origem": "",
            "Quadra" : "",
            "Lote": "",
            "Tributo": "",
            "Ano": "",
            "Mês": "",
            "Situação": "",
            "Valor Atual": total_valor_desconhecida,
            "Juros": total_juros_desconhecida,
            "Multa": total_multa_desconhecida,
            "Total Divida": total_divida_deconhecida,
            "Vencidas": "",
            "A Vencer": "",
            "Endereço": ""
        }
        resultados_dividas_nao_identificadas = pd.DataFrame([resultados_dividas_nao_identificadas])
        df_dividas_nao_identificadas = pd.concat([df_dividas_nao_identificadas, resultados_dividas_nao_identificadas], ignore_index=True)
    
    return df_final, df_iss, df_dividas_nao_identificadas


@app.route("/anapolis", methods=["POST"])
def upload_file():
   
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files["file"]
    
    if file.filename == "":
        return "No selected file"
    
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(pdf_path)
 
    CSV = "../../Dados/data.csv"
    
    df_final, df_iss, df_dividas_nao_identificadas = processamento_dividas(pdf_path, CSV)
    
    ramdom_numbers = "".join(random.choices(string.digits, k=8))
    
    excel_final_filename = f"Dividas-de-Unidades({ramdom_numbers}).xlsx"
    excel_iss_filename = f"Dividas-Diversas({ramdom_numbers}).xlsx"
    excel_dividas_nao_identificadas_filename = f"Dividas-Não-Identificadas({ramdom_numbers}).xlsx"
    
    excel_final_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_final_filename)
    excel_iss_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_iss_filename)
    excel_dividas_nao_identificadas_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_dividas_nao_identificadas_filename)
    
    with pd.ExcelWriter(excel_final_path, engine="xlsxwriter") as writer:
        df_final.to_excel(writer, index=False)
        print("Arquivo Excel df_final salvo com sucesso!")

        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        
        blue_format = workbook.add_format({"bg_color": "#C6E2FF", "align": "left"})
        white_format = workbook.add_format({"bg_color": "#FEFEFE", "align": "left"})
        bold_format = workbook.add_format({"bold": True, "bg_color": "#666666", "color": "#ffffff", "align": "left"})

        for row_num in range(1, len(df_final) + 1):
            if row_num % 2 == 0:
                worksheet.set_row(row_num, cell_format=blue_format)
            else:
                worksheet.set_row(row_num, cell_format=white_format)

            if df_final.iloc[row_num - 1]["Inscrição"] == "Totais R$:":
                worksheet.set_row(row_num, cell_format=bold_format)
        
        worksheet.set_column("A:A", 16)
        worksheet.set_column("B:B", 16)
        worksheet.set_column("F:F", 16)
        worksheet.set_column("I:I", 14)
        worksheet.set_column("G:H", 6)
        worksheet.set_column("J:J", 10)
        worksheet.set_column("M:M", 10)
        worksheet.set_column("P:P", 32)
        worksheet.set_column("Q:Q", 12)
        worksheet.set_column("R:R", 32)
        worksheet.set_column("S:S", 20)
        worksheet.set_column("T:T", 12)
        worksheet.set_column("U:V", 18)
        worksheet.set_column("X:X", 28)
        worksheet.set_column("Y:Y", 10)
        worksheet.set_column("Z:Z", 12)
        worksheet.set_column("AB:AB", 86)
    
    with pd.ExcelWriter(excel_iss_path, engine="xlsxwriter") as writer:
        df_iss.to_excel(writer, index=False)
        print("Arquivo Excel df_iss salvo com sucesso!")

        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]

        blue_format = workbook.add_format({"bg_color": "#C6E2FF", "align": "left"})
        white_format = workbook.add_format({"bg_color": "#FEFEFE", "align": "left"})
        bold_format = workbook.add_format({"bold": True, "bg_color": "#666666", "color": "#ffffff", "align": "left"})

        for row_num in range(1, len(df_iss) + 1):
            if row_num % 2 == 0:
                worksheet.set_row(row_num, cell_format=blue_format)
            else:
                worksheet.set_row(row_num, cell_format=white_format)

            if df_iss.iloc[row_num - 1]["Inscrição"] == "Totais R$:":
                worksheet.set_row(row_num, cell_format=bold_format)

        worksheet.set_column("B:B", 12)
        worksheet.set_column("E:E", 14)
        worksheet.set_column("H:H", 16)
        worksheet.set_column("I:I", 10)
        worksheet.set_column("L:L", 10)
        worksheet.set_column("O:O", 86)
    
    with pd.ExcelWriter(excel_dividas_nao_identificadas_path, engine="xlsxwriter") as writer:
        df_dividas_nao_identificadas.to_excel(writer, index=False)
        print("Arquivo Excel Dividas Desconhecidas salvo com sucesso!")

        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]

        blue_format = workbook.add_format({"bg_color": "#C6E2FF", "align": "left"})
        white_format = workbook.add_format({"bg_color": "#FEFEFE", "align": "left"})
        bold_format = workbook.add_format({"bold": True, "bg_color": "#666666", "color": "#ffffff", "align": "left"})

        for row_num in range(1, len(df_dividas_nao_identificadas) + 1):
            if row_num % 2 == 0:
                worksheet.set_row(row_num, cell_format=blue_format)
            else:
                worksheet.set_row(row_num, cell_format=white_format)

            if df_dividas_nao_identificadas.iloc[row_num - 1]["Inscrição"] == "Totais R$:":
                worksheet.set_row(row_num, cell_format=bold_format)

        worksheet.set_column("A:A", 16)
        worksheet.set_column("B:B", 12)
        worksheet.set_column("E:E", 14)
        worksheet.set_column("H:H", 16)
        worksheet.set_column("I:I", 10)
        worksheet.set_column("L:L", 10)
        worksheet.set_column("O:O", 86)
        
    zip_filename = f"Extrato de Débitos({ramdom_numbers}).zip"
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(excel_final_path, os.path.basename(excel_final_path))
        zip_file.write(excel_iss_path, os.path.basename(excel_iss_path))
        zip_file.write(excel_dividas_nao_identificadas_path, os.path.basename(excel_dividas_nao_identificadas_path))
    
    response = send_file(zip_path, as_attachment=True)
   
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)