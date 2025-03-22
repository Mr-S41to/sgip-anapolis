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

    with open(pdf_path, "rb") as file_pdf:
        reader_pdf = PdfReader(file_pdf)
        num_paginas = len(reader_pdf.pages)

        text = ""
        imoveis = []

        for num_pagina in range(num_paginas):
            pagina = reader_pdf.pages[num_pagina]
            text = pagina.extract_text()
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
            text = re.sub(r"\n(.+?)BAIRRO:", "", text, flags=re.MULTILINE)
            text = re.sub(r"RUA(.+?)\n", "", text, flags=re.MULTILINE)
            text = re.sub(r"A.\sI.", "A.I.", text, flags=re.MULTILINE)
            text = re.sub(
                r"\b(TX)\s+(EXP)\s+(ALV)\b", r"\1\2\3", text, flags=re.MULTILINE
            )
            text = re.sub(r"\b(ISS)\s+(RET)\b", r"\1\2", text, flags=re.MULTILINE)
            text = re.sub(r"^Inicio\sAtividade:.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(r"^CORRETAGEM.*$", "\n", text, flags=re.MULTILINE)
            text = re.sub(r"QD\.\:", "QD.", text, flags=re.MULTILINE)
            text = re.sub(r"LT\.\:", "LT.", text, flags=re.MULTILINE)
            text = re.sub(r"\n(.+?)Página", "\n", text, flags=re.MULTILINE)
            text = re.sub(r"ADC:(.+?)\n\n", "\n", text, flags=re.DOTALL)
            text = re.sub(r"\n+", "\n", text)
            text = re.sub(
                r"EXTRATO\sDE\sDÉBITO", "\nEXTRATO DE DÉBITO", text, flags=re.MULTILINE
            )
            print(text)

            padrao_data = re.compile(r"EXTRATO DE DÉBITO(.+?)(?=EXTRATO DE DÉBITO|$)", re.DOTALL)
            correspondencia_data = padrao_data


            ocorrencias_dividas = correspondencia_data.findall(text)

            for ocorrencia_divida in ocorrencias_dividas:
                
                dividas = []

                padrao_inscricao_cci = re.compile(r"Inscrição:\s(\d+)\sCCI:", re.DOTALL)
                correspondencia_incricao_cci = padrao_inscricao_cci.search(ocorrencia_divida)

                if correspondencia_incricao_cci:
                    inscricao_cci = correspondencia_incricao_cci.group(1)
                    print("Número de inscrição CCI:", inscricao_cci)
                else:
                    inscricao_cci = None
                    print("Número de inscrição CCI não encontrado.")

                padrao_local = re.compile(r"\n(.+?),", re.DOTALL)
                correspondencia_local = padrao_local.search(ocorrencia_divida)

                if correspondencia_local:
                    local = correspondencia_local.group(1)
                else:
                    local = None

                padrao_quadra = re.compile(r"Qd.:\s(.+?),", re.DOTALL)
                correspondencia_quadra = padrao_quadra.search(ocorrencia_divida)

                if correspondencia_quadra:
                    quadra = correspondencia_quadra.group(1)
                else:
                    quadra = None

                padrao_lote = re.compile(r"Lt.:\s(.+?),", re.DOTALL)
                correspondencia_lote = padrao_lote.search(ocorrencia_divida)

                if correspondencia_lote:
                    lote = correspondencia_lote.group(1)
                else:
                    lote = None

                padrao_bairro = re.compile(r"CCI:\s(.+?)\n", re.DOTALL)
                correspondencia_bairro = padrao_bairro.search(ocorrencia_divida)

                if correspondencia_bairro:
                    bairro = correspondencia_bairro.group(1)
                else:
                    bairro = None

                padrao_cidade = re.compile(r"CIDADE:\s(.+?),", re.DOTALL)
                correspondencia_cidade = padrao_cidade.search(ocorrencia_divida)

                if correspondencia_cidade:
                    cidade = correspondencia_cidade.group(1)
                else:
                    cidade = None

                data_dividas = re.findall(
                    r"PE.*?\w\s-\s\d+", ocorrencia_divida, re.DOTALL
                )

                for linha in data_dividas:
                    total_dividas = 0
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
                        [valor_tributo, base, juros, multa, total, correcao, desconto]
                    )
                    
                    divida = {
                        "Inscrição": inscricao_cci,
                        "Local": local,
                        "Quadra": quadra,
                        "Lote": lote,
                        "Status": status,
                        "Parcela": parcela,
                        "Alíquota": porcentagem,
                        "Multa": multa,
                        "Valor Tributo": valor_tributo,
                        "Vencimento": vencimento,
                        "Tributo": tributo,
                        "Correção": correcao,
                        "Juros": juros,
                        "Débito": debito,
                        "Ref": ref,
                        "Descontos": desconto,
                        "Total Divida": total,
                        "Bairro": bairro
                    }
                    dividas.append(divida)

                imovel = {
                    "Dividas": dividas,
                }
                imoveis.append(imovel)
                
    dfs = []
    df_dividas_desconhecidas = []

    for imovel in imoveis:
        dividas = imovel["Dividas"]

        for divida in dividas:
            df = pd.DataFrame(
                [divida],
                columns=[
                    "Inscrição",
                    "Quadra",
                    "Lote",
                    "Tributo",
                    "Ref",
                    "Parcela",
                    "Valor Tributo",
                    "Alíquota",
                    "Juros",
                    "Multa",
                    "Correção",
                    "Descontos",
                    "Total Divida",
                    "Vencimento",
                    "Bairro"
                ],
            )
        
            if any(df["Inscrição"].isin(df_csv["NMINSCRICAOIMOBILIARIA"])):
                dfs.append(df)
                indices_correspondentes = df[df["Inscrição"].isin(df_csv["NMINSCRICAOIMOBILIARIA"])].index
                valores_correspondentes = csv_data.loc[df_csv["NMINSCRICAOIMOBILIARIA"].isin(df["Inscrição"])]
                
                for indexs in indices_correspondentes:
                    for coluna in csv_data.columns:
                        df.at[indexs, coluna] = valores_correspondentes[coluna].values[0]
        
            if all(~df["Inscrição"].isin(df_csv["NMINSCRICAOIMOBILIARIA"])):
                df_dividas_desconhecidas.append(df)

    if not dfs:
        df_final = pd.DataFrame([{
            "Inscrição": "-", 
            "Quadra": "-", 
            "Lote": "-", 
            "Tributo": "-", 
            "Ref": "-", 
            "Parcela": "-", 
            "Valor Tributo": "-", 
            "Alíquota": "-", 
            "Juros": "-",
            "Multa": "-", 
            "Correção": "-", 
            "Descontos": "-", 
            "Total Divida": "-", 
            "Vencimento": "-", 
            "Bairro": "-"
        }])
        
        resultados = {
            "Inscrição": "Totais R$:", 
            "Quadra": "-", 
            "Lote": "-", 
            "Tributo": "-", 
            "Ref": "-", 
            "Parcela": "-", 
            "Valor Tributo": "-", 
            "Alíquota": "-", 
            "Juros": "-",
            "Multa": "-", 
            "Correção": "-", 
            "Descontos": "-", 
            "Total Divida": "-", 
            "Vencimento": "-", 
            "Bairro": "-"
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
            "Tributo", 
            "Ref",
            "Parcela",
            "Valor Tributo", 
            "Alíquota", 
            "Juros", 
            "Multa", 
            "Correção", 
            "Descontos", 
            "Total Divida",
            "Vencimento", 
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
            "Bairro",
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
            "NMCLIENTE": "Cliente",
            "CIDADE": "Cidade",
            "QTAREAPRIV": "Área Priv.",
            "QTAREACOMUM": "Área Com.",
        })
        
        order = [
            "Observação", 
            "Inscrição",
            "Quadra",
            "Lote",
            "Tributo", 
            "Ref",
            "Parcela",
            "Valor Tributo", 
            "Alíquota", 
            "Juros", 
            "Multa", 
            "Correção", 
            "Descontos", 
            "Total Divida",
            "Vencimento", 
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
            "Bairro"
        ]
        df_final = df_final.reindex(columns=order)
        df_final = df_final[order]  
        
        total_divida = df_final["Total Divida"].sum()
        total_multa = df_final["Multa"].sum()
        total_juros = df_final["Juros"].sum()
        total_valor = df_final["Valor Tributo"].sum()
        total_correcao = df_final["Correção"].sum()
        total_descontos = df_final["Descontos"].sum()
        
        resultados = {
            "Observação" : "", 
            "Inscrição": "Totais R$:",
            "Quadra" : "",
            "Lote" : "",
            "Tributo" : "", 
            "Ref" : "",
            "Parcela" : "",
            "Valor Tributo" : total_valor,
            "Alíquota" : "",
            "Juros"  : total_juros,
            "Multa" : total_multa, 
            "Correção" : total_correcao, 
            "Descontos" : total_descontos,
            "Total Divida" : total_divida, 
            "Vencimento" : "", 
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
            "Bairro" : ""
        }
        resultados_df = pd.DataFrame([resultados])
        df_final = pd.concat([df_final, resultados_df], ignore_index=True)
        
    if not df_dividas_desconhecidas:
        df_dividas_desconhecidas = pd.DataFrame([{
            "Inscrição": "-", 
            "Quadra": "-", 
            "Lote": "-", 
            "Tributo": "-", 
            "Ref": "-", 
            "Parcela": "-", 
            "Valor Tributo": "-", 
            "Alíquota": "-", 
            "Juros": "-",
            "Multa": "-", 
            "Correção": "-", 
            "Descontos": "-", 
            "Total Divida": "-", 
            "Vencimento": "-", 
            "Bairro": "-"
        }])
        
        resultados_dividas_desconhecidas = {
            "Inscrição": "R$ Totais R$:", 
            "Quadra": "-", 
            "Lote": "-", 
            "Tributo": "-", 
            "Ref": "-", 
            "Parcela": "-", 
            "Valor Tributo": "-", 
            "Alíquota": "-", 
            "Juros": "-",
            "Multa": "-", 
            "Correção": "-", 
            "Descontos": "-", 
            "Total Divida": "-", 
            "Vencimento": "-", 
            "Bairro": "-"
        }
        resultados_dividas_desconhecidas = pd.DataFrame([resultados_dividas_desconhecidas])
        df_dividas_desconhecidas = pd.concat([df_dividas_desconhecidas, resultados_dividas_desconhecidas], ignore_index=True)
    else:
        df_dividas_desconhecidas = pd.concat(df_dividas_desconhecidas, ignore_index=True)
    
        total_divida_desconhecidas = df_dividas_desconhecidas["Total Divida"].sum()
        total_multa_desconhecidas = df_dividas_desconhecidas["Multa"].sum()
        total_juros_desconhecidas = df_dividas_desconhecidas["Juros"].sum()
        total_valor_deconhecidos = df_dividas_desconhecidas["Valor Tributo"].sum()
        total_correcao_desconhecidas = df_dividas_desconhecidas["Correção"].sum()
        total_descontos_desconhecidas = df_dividas_desconhecidas["Descontos"].sum()
    
        resultados_dividas_desconhecidas = {
            "Inscrição": "Totais R$:",
            "Quadra" : "",
            "Lote" : "",
            "Tributo" : "", 
            "Ref" : "",
            "Parcela" : "",
            "Valor Tributo" : total_valor_deconhecidos,
            "Alíquota" : "",
            "Juros"  : total_juros_desconhecidas,
            "Multa" : total_multa_desconhecidas, 
            "Correção" : total_correcao_desconhecidas, 
            "Descontos" : total_descontos_desconhecidas,
            "Total Divida" : total_divida_desconhecidas, 
            "Vencimento" : "", 
            "Bairro" : ""
        }
    resultados_dividas_desconhecidas = pd.DataFrame([resultados_dividas_desconhecidas])
    df_dividas_desconhecidas = pd.concat([df_dividas_desconhecidas, resultados_dividas_desconhecidas], ignore_index=True)
    
    return df_final, df_dividas_desconhecidas

@app.route("/jatai", methods=["POST"])
def upload_file():
    
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files["file"]
    
    if file.filename == "":
        return "No selected file"
    
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(pdf_path)

    CSV = "data.csv"
    
    df_final, df_dividas_desconhecidas = processamento_dividas(pdf_path, CSV)
    
    ramdom_numbers = "".join(random.choices(string.digits, k=8))

    excel_final_filename = f"Dividas-de-Unidades({ramdom_numbers}).xlsx"
    excel_dividas_desconhecidas_filename = f"Dividas-Não-Identificadas({ramdom_numbers}).xlsx"
     
    excel_final_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_final_filename)
    excel_dividas_desconhecidas_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_dividas_desconhecidas_filename)
    
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
        
        worksheet.set_column("A:B", 16)
        worksheet.set_column("D:D", 16)
        worksheet.set_column("F:M", 10)
        worksheet.set_column("N:O", 12)
        worksheet.set_column("P:P", 32)
        worksheet.set_column("P:P", 32)
        worksheet.set_column("Q:Q", 12)
        worksheet.set_column("R:R", 32)
        worksheet.set_column("S:S", 16)
        worksheet.set_column("T:V", 12)
        worksheet.set_column("X:X", 32)
        worksheet.set_column("Z:AA", 16)
        worksheet.set_column("AB:AB", 48)

    with pd.ExcelWriter(excel_dividas_desconhecidas_path, engine="xlsxwriter") as writer:
        df_dividas_desconhecidas.to_excel(writer, index=False)
        print("Arquivo Excel Dividas Desconhecidas salvo com sucesso!")

        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]

        blue_format = workbook.add_format({"bg_color": "#C6E2FF", "align": "left"})
        white_format = workbook.add_format({"bg_color": "#FEFEFE", "align": "left"})
        bold_format = workbook.add_format({"bold": True, "bg_color": "#666666", "color": "#ffffff", "align": "left"})

        for row_num in range(1, len(df_dividas_desconhecidas) + 1):
            if row_num % 2 == 0:
                worksheet.set_row(row_num, cell_format=blue_format)
            else:
                worksheet.set_row(row_num, cell_format=white_format)

            if df_dividas_desconhecidas.iloc[row_num - 1]["Inscrição"] == "Totais R$:":
                worksheet.set_row(row_num, cell_format=bold_format)

        worksheet.set_column("A:A", 16)
        worksheet.set_column("D:D", 16)
        worksheet.set_column("F:M", 10)
        worksheet.set_column("N:N", 12)
        worksheet.set_column("O:O", 86)

    zip_filename = f"Extrato de Débitos({ramdom_numbers}).zip"
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(excel_final_path, os.path.basename(excel_final_path))
        zip_file.write(excel_dividas_desconhecidas_path, os.path.basename(excel_dividas_desconhecidas_path))
    
    response = send_file(zip_path, as_attachment=True)
   
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)