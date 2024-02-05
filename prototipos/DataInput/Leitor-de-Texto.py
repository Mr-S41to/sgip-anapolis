from PyPDF2 import PdfReader
import re
import pandas as pd

def processamento_dividas(PDF):
    # Abrir pedef em Binários.
    with open(PDF, 'rb') as file_pdf:
        reader_pdf = PdfReader(file_pdf)
        num_paginas = len(reader_pdf.pages)

        text = ''
        imoveis = []
        iss = []
        
        # Iterando entre paginas do PDF.
        for num_pagina in range(num_paginas):
            pagina = reader_pdf.pages[num_pagina]
            # Extração do texto das paginas
            text += pagina.extract_text()
            # Debugging de leitura de arquivo.
            # print(text)
            
        text = re.sub(r'\.(\s*\.)+', '\n', text)
        text = re.sub(r'ANO MÊS TRIBUTO VL. ATUAL. JUROS MULTA TOTAL VENCIDAS / A VENCER', '\n', text)
        text = re.sub(r'^.*TOTAL:$', '\n', text, flags=re.MULTILINE)
        # text = re.sub(r'^TOTAL ORIGEM:.*$', '\n', text, flags=re.MULTILINE)
        text = re.sub(r'^.*ANÁPOLIS$', '\n', text, flags=re.MULTILINE)
        text = re.sub(r'^Página.*$', '\n', text, flags=re.MULTILINE)
        text = re.sub(r'^Data:.*$', '\n', text, flags=re.MULTILINE)
        # text = re.sub(r'Total Dívida Corrente:.*?OBSERVAÇÃO:.*', '\n', text, flags=re.DOTALL)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        text = re.sub(r'(Endereço:)', r'\n\n\1', text)

        print(text)
        
        padrao_origem = re.compile(r'Inscrição:\s*(.+?)\s*Origem:')
        padrao_inscricao = re.compile(r'Matrícula:\s*(.+?)\s*Inscrição:')
        padrao_endereco = re.compile(r'Endereço:\s*(.+?)(?=\d{3}\.\d{3}\.\d{4}\.\d{3}\s*Matrícula:)')
        padrao_matricula = re.compile(r'Endereço:.*?(\d{3}\.\d{3}\.\d{4}\.\d{3})\s*Matrícula:')
        padrao_data = re.compile(r'Origem:(.+?)Endereço:', re.DOTALL)
            
        # Correspondencia de Headers.
        correspondencia_origem = padrao_origem.findall(text)
        correspondencia_inscricao = padrao_inscricao.findall(text)
        correspondencia_endereco = padrao_endereco.findall(text)
        correspondencia_matricula = padrao_matricula.findall(text)
        correspondencia_data = padrao_data.findall(text)
        
        padrao_data_iss = re.compile(r'ISS Origem:(.+?)Total Dívida Corrente:', re.DOTALL)
        correspondencia_data_iss = padrao_data_iss.findall(text)
        
        for iss_data_list in zip(
            correspondencia_data_iss
        ):
            iss_data = iss_data_list[0].replace(r'\n', '\n')
            # iss_data = iss_data.replace(r'\n', '\n')
            print("\nFumaça")
            print(iss_data)
            
            dividas_iss = []
            total_iss = 0
            
            padrao_dividas_iss = re.compile(r'Situação:\s*(.+?)TOTAL ORIGEM:', re.DOTALL)
            padrao_situacao_iss = re.compile(r'\n*(.+?)\s*Situação:')
            correspondencia_situacao_iss = padrao_situacao_iss.findall(iss_data)
            correspondencia_dividas_iss = padrao_dividas_iss.findall(iss_data)
            
            if correspondencia_dividas_iss and correspondencia_situacao_iss:
                for dividas_contribuinte in correspondencia_dividas_iss:
                    situacao_iss = correspondencia_situacao_iss[0].strip() if correspondencia_situacao_iss else None
                    divida_iss = []
                    total_divida_iss = 0
                            
                    for linha in dividas_contribuinte.strip().split('\n'):
                        padrao_linha = re.compile(r'(\d{4}) (\d{2}) (.*?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d+) (\d+)')
                        correspondencia_linha = padrao_linha.match(linha)
                                
                        if correspondencia_linha:
                            ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer = correspondencia_linha.groups()
                            valor_atual = valor_atual.replace(".", "").replace(",",".")
                            juros = juros.replace(".", "").replace(",", ".")
                            multa = multa.replace(".", "").replace(",",".")
                            total = total.replace(".", "").replace(",",".")
                            ano, mes, tributo = map(str, [ano, mes, tributo])
                            valor_atual, juros, multa = map(float, [valor_atual, juros, multa])
                            vencidas, a_vencer = map(int, [vencidas, a_vencer])
                            # total_divida += float(total)
                            divida_iss.append({
                                "Ano": ano,
                                "Mês": mes,
                                "Tributo": tributo,
                                "Valor Atual": valor_atual,
                                "Juros": juros,
                                "Multa": multa,
                                "Total": total,
                                "Vencidas": vencidas,
                                "A Vencer": a_vencer
                            })
                    total_iss += float(total_divida_iss)
                    dividas_iss.append({
                        "Situação-ISS": situacao_iss, 
                        "Divida-ISS": divida_iss
                    })
            iss.append({
                "Dividas-ISS": dividas_iss
            })
                    
        for origem, inscricao, endereco, matricula, data in zip(
            correspondencia_origem,
            correspondencia_inscricao,
            correspondencia_endereco,
            correspondencia_matricula,
            correspondencia_data
        ):
            origem = origem.strip()
            endereco = endereco.strip()
            inscricao = inscricao.strip()
            matricula = matricula.strip()
            
            padrao_dividas = re.compile(r'Situação:\s*(.+?)TOTAL ORIGEM:', re.DOTALL)
            padrao_situacao = re.compile(r'\n*(.+?)\s*Situação:')
            correspondencia_situacao = padrao_situacao.findall(data)
            correspondencia_dividas = padrao_dividas.findall(data)
                            
            dividas = []
            total_origem = 0
                            
            if correspondencia_dividas and correspondencia_situacao:
                for dividas_cliente in correspondencia_dividas:
                    situacao = correspondencia_situacao[0].strip() if correspondencia_situacao else None
                    divida = []
                    total_divida = 0
                            
                    for linha in dividas_cliente.strip().split('\n'):
                        padrao_linha = re.compile(r'(\d{4}) (\d{2}) (.*?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d+) (\d+)')
                        correspondencia_linha = padrao_linha.match(linha)
                                
                        if correspondencia_linha:
                            ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer = correspondencia_linha.groups()
                            valor_atual = valor_atual.replace(".", "").replace(",",".")
                            juros = juros.replace(".", "").replace(",", ".")
                            multa = multa.replace(".", "").replace(",",".")
                            total = total.replace(".", "").replace(",",".")
                            ano, mes, tributo = map(str, [ano, mes, tributo])
                            valor_atual, juros, multa = map(float, [valor_atual, juros, multa])
                            vencidas, a_vencer = map(int, [vencidas, a_vencer])
                            total_divida += float(total)
                            divida.append({
                                "Ano": ano,
                                "Mês": mes,
                                "Tributo": tributo,
                                "Valor Atual": valor_atual,
                                "Juros": juros,
                                "Multa": multa,
                                "Total": total,
                                "Vencidas": vencidas,
                                "A Vencer": a_vencer
                            })
                            
                    total_origem += float(total_divida)
                    dividas.append({
                        "Situação": situacao, 
                        "Divida": divida,
                        "Total Origem": total_origem
                    })
                            
            imoveis.append({
                "Origem": origem,
                "Inscrição": inscricao,
                "Matrícula": matricula,
                "Endereço": endereco,
                "Dívidas": dividas,
                # "Data": data
            })
            
    return imoveis, iss

PDF = "sample.pdf"
imoveis_resultados, iss_resultados = processamento_dividas(PDF)

# Depuração de resultados.
# for i, imovel in enumerate(imoveis_resultados, start=1):
#     origem = imovel['Origem']
#     inscricao = imovel['Inscrição']
#     matricula = imovel['Matrícula']
#     endereco = imovel['Endereço']
#     dividas = imovel['Dívidas']
    
    # print(f"\n{i}\nDividas por Cliente:\nOrigem: {origem} Inscrição: {inscricao} Matrícula: {matricula}\nEndereço: {endereco}\nData: {dividas}")

for j, imposto in enumerate(iss_resultados, start=1):
    dividas_iss = imposto['Dividas-ISS']
    print(dividas_iss)


# print(f"\nTotal Solicitante: {total_solicitante}")

# Criar DataFrame
# df = pd.DataFrame(imoveis, columns=["Origem", "Inscrição",  "Endereço", "Matrícula", "Dívidas"])

# Transformar a coluna "Dívidas" em string para evitar problemas com listas
# df["Dívidas"] = df["Dívidas"].astype(str)

# Depuração do DataFrame
# print("\n", df)

# # Salvando arquivo .CSV
# df.to_csv("Relatório.csv", index=False)
# print("Arquivo CSV Salvo com sucesso!")

# # Salvando arquivo em formato Excel
# Excel = "Relatório.xlsx"
# df.to_excel(Excel, index=False)
# print("Excel Salvo com sucesso!")