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
            print(text)
            
        text = re.sub(r'\.(\s*\.)+', '\n', text)
        text = re.sub(r'ANO MÊS TRIBUTO VL. ATUAL. JUROS MULTA TOTAL VENCIDAS / A VENCER', '\n', text)
        text = re.sub(r'^.*TOTAL:$', '\n', text, flags=re.MULTILINE)
        # text = re.sub(r'^TOTAL ORIGEM:.*$', '\n', text, flags=re.MULTILINE)
        text = re.sub(r'^.*ANÁPOLIS$', '\n', text, flags=re.MULTILINE)
        text = re.sub(r'^Página.*$', '\n', text, flags=re.MULTILINE)
        text = re.sub(r'^Data:.*$', '\n', text, flags=re.MULTILINE)
        # text = re.sub(r'Total Dívida Corrente:.*?OBSERVAÇÃO:.*', '\n\n\1', text, flags=re.DOTALL)
        text = re.sub(r',\s(.+?)Matrícula:\s', '\n', text, flags=re.MULTILINE)
        text = re.sub(r';\s(.+?)Matrícula:\s', '\n', text, flags=re.MULTILINE)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        text = re.sub(r'(Endereço:)', r'\n\n\1', text)
        text = re.sub(r'(Total Dívida Corrente:)', r'\n\n\1', text)

        print(text)
        
        padrao_origem = re.compile(r'Inscrição:\s(.+?)\sOrigem:')
        padrao_inscricao = re.compile(r'\n(.+?)\s*Inscrição:')
        padrao_endereco = re.compile(r'Endereço:\s*(.+?)\n')
        padrao_data = re.compile(r'Origem:(.+?)\n\n', re.DOTALL)
            
        # Correspondencia de Headers.
        correspondencia_origem = padrao_origem.findall(text)
        correspondencia_inscricao = padrao_inscricao.findall(text)
        correspondencia_endereco = padrao_endereco.findall(text)
        correspondencia_data = padrao_data.findall(text)
                    
        for origem, endereco, inscricao, data in zip(
            correspondencia_origem,
            correspondencia_endereco,
            correspondencia_inscricao,
            correspondencia_data
        ):
            # origem = origem.strip()
            # endereco = endereco.strip()
            # inscricao = inscricao.strip()
            
            print("\n-----Dados-----", data)
            padrao_quadra = re.compile(r'Q[Dd].\s(.+?)\s')
            padrao_lote = re.compile(r'L[Tt].(.+?)\s')
            
            correspondencia_quadra = padrao_quadra.findall(endereco)
            correspondencia_lote = padrao_lote.findall(endereco)
            
            quadra = correspondencia_quadra[0].strip()
            lote = correspondencia_lote[0].strip()
            # print(quadra, lote)
                       
            data = re.sub(r'(Dívida)', r'\n\n\1', data)
            data = re.sub(r'(Ajuizada)', r'\n\n\1', data)
            data = re.sub(r'^TOTAL ORIGEM:.*$', '\n', data, flags=re.MULTILINE)          
            
            padrao_dividas = re.compile(r'\n(.+?)\n\n', re.DOTALL)
            correspondencia_dividas = padrao_dividas.findall(data)
                          
            dividas = []
            total_origem = 0
                            
            if correspondencia_dividas:
                for dividas_cliente in correspondencia_dividas:                    

                    padrao_situacao = re.compile(r'\n*(.+?)Situação:')
                    correspondencia_situacao = padrao_situacao.findall(dividas_cliente)
                    situacao = correspondencia_situacao[0].strip() 
                        
                    divida = []
                    total_dividas = 0
                            
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
                            valor_atual, juros, multa, total = map(float, [valor_atual, juros, multa, total])
                            vencidas, a_vencer = map(int, [vencidas, a_vencer])
                            total_dividas += float(total)
                            divida.append({
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
                                "A Vencer": a_vencer
                            })
                            
                    total_origem += float(total_dividas)
                    dividas.append({
                        "Divida": divida,
                        "Total Origem": total_origem
                    })
                            
            imoveis.append({
                "Inscrição": inscricao,
                "Dívidas": dividas
            })
                      
    return imoveis

PDF = "02.pdf"
imoveis_resultados = processamento_dividas(PDF)

# Depuração de resultados.
dfs = []

# Depuração de resultados.
for i, imovel in enumerate(imoveis_resultados, start=1):
    inscricao = imovel['Inscrição']
    dividas = imovel['Dívidas']
    
    for divida in dividas:
        df = pd.DataFrame(divida['Divida'], columns=["Inscrição", "Quadra", "Lote", "Origem", "Tributo", "Ano", "Mês",  "Situação", "Valor Atual", "Juros", "Multa", "Total Divida", "Vencidas", "A Vencer"])               
        
        # Adicionando o DataFrame atual à lista
        dfs.append(df)

# Concatenando todos os DataFrames na lista em um único DataFrame
df_final = pd.concat(dfs, ignore_index=True)

# Depuração do DataFrame final
print(df_final)

# Salvando arquivo .CSV
df_final.to_csv("RelatórioFinal.csv", index=False)
print("Arquivo CSV Salvo com sucesso!")

# Salvando arquivo em formato Excel
Excel = "RelatórioFinal.xlsx"
df_final.to_excel(Excel, index=False)
print("Arquivo Excel Salvo com sucesso!")