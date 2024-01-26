from PyPDF2 import PdfReader
import re
import pandas as pd

# Abrir pedef em Binários.
with open("sample.pdf", 'rb') as file_pdf:
    reader_pdf = PdfReader(file_pdf)

    num_paginas = len(reader_pdf.pages)

    # Define a pattern to extract address information.
    padrao_origem = re.compile(r'Inscrição:\s*(.+?)\s*Origem:')
    padrao_inscricao = re.compile(r'Matrícula:\s*(.+?)\s*Inscrição:')
    padrao_matricula = re.compile(r'Endereço:.*?(\d{3}\.\d{3}\.\d{4}\.\d{3})\s*Matrícula:' or r'Endereço:\s*(.+?)\s*Matrícula:')
    padrao_endereco = re.compile(r'Endereço:\s*(.+?)\s*(?=\d{3}\.\d{3}\.\d{4}\.\d{3}\s*Matrícula:)')
    # Ajustado para excluir o numero de Matrículas.
    padrao_data = re.compile(r'Origem:(.*?)Endereço:', re.DOTALL)
    padrao_dividas = re.compile(r'Situação:\s*(.+?)\n\n', re.DOTALL)
    padrao_situacao = re.compile(r'\n*(.+?)\s*Situação:')
    # padrao_linha = re.compile(r'(\d{4}) (\d{2}) (.*?) (\d+(?:,\d+)?) (\d+(?:,\d+)?) (\d+(?:,\d+)?) (\d+(?:,\d+)?) (\d+) (\d+)')
    # padrao_linha = re.compile(
    #     r'(\d{4}) (\d{2}) (IPTU|TSU|CIP|IPTU - DA|TSU - DA|CIP - DA|Parcelamento DA|Saldo Parc\. DCC|Saldo Parc\. D\.A|Capin\. RoçaD\.A|Capinação e Roç|Parcelam/Div/Aj) (\d{1,3}(?:\.\d{3})*(?:,\d+)?)|([\d.,]+) (\d{1,3}(?:\.\d{3})*(?:,\d+)?)|([\d.,]+) (\d{1,3}(?:\.\d{3})*(?:,\d+)?)|([\d.,]+) (\d{1,3}(?:\.\d{3})*(?:,\d+)?)|([\d.,]+) (\d+) (\d+)'
    # )
    padrao_linha = re.compile(r'(\d{4}) (\d{2}) (.*?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d+) (\d+)')
    
    # The extracted objects will be stored in this list.
    imoveis = []

    # Iterate through the pages of the PDF.
    for num_pagina in range(num_paginas):
        pagina = reader_pdf.pages[num_pagina]

        # Extract text from the page.
        text = pagina.extract_text()

        # Debugging de leitura de arquivo.
        print(f"Texto da página {num_pagina + 1}:\n{text}\n")

        # Correspondencia de Headers.
        correspondencia_origem = padrao_origem.findall(text)
        correspondencia_inscricao = padrao_inscricao.findall(text)
        correspondencia_matricula = padrao_matricula.findall(text)
        correspondencia_endereco = padrao_endereco.findall(text)

        # Process each match.
        for origem, inscricao, endereco, matricula in zip(
            correspondencia_origem,
            correspondencia_inscricao,
            correspondencia_endereco,
            correspondencia_matricula
        ):
            origem = origem.strip()
            inscricao = inscricao.strip()
            if correspondencia_matricula:   
                matricula = matricula.strip()
            else:
                matricula = None
            endereco = endereco.strip()

            correspondencia_data = padrao_data.search(text)
            # Verificação de correspondencia de dados.
            if correspondencia_data:
                # Obterndo correspondencia de dados.
                data = correspondencia_data.group(1).strip()
            else:
                data = "Padrão de dados em 'data' não encontrado."
            # Formatando os dados.
            data = re.sub(r'\.(\s*\.)+', '', data)
            data = re.sub(r'ANO MÊS TRIBUTO VL. ATUAL. JUROS MULTA TOTAL VENCIDAS / A VENCER', '', data)
            data = re.sub(r'^.*TOTAL:$', '', data, flags=re.MULTILINE)
            data = re.sub(r'^TOTAL ORIGEM:.*$', '', data, flags=re.MULTILINE)
            
            situacao = None
            dividas = []
            divida = []
            detalhes_divida = []
            # correspondencia_situacao = padrao_situacao.findall(data)
            # if correspondencia_situacao:
            #     situacao = correspondencia_situacao[0].strip()
            
            #     for situacao in correspondencia_situacao:
            #         correspondencia_dividas = padrao_dividas.findall(data)
            #         if correspondencia_dividas:
                        
            #             for dividas_cliente in correspondencia_dividas:
            #                 for linha in dividas_cliente.strip().split('\n'):
            #                     correspondencia_linha = padrao_linha.match(linha)
            #                     if correspondencia_linha:
            #                         ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer = correspondencia_linha.groups()
            #                         divida.append([ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer])
            #                     else:
            #                         divida.append([ano or None, mes or None, tributo or None, valor_atual or None, juros or None, multa or None, total or None, vencidas or None, a_vencer or None])
            #             dividas.append((situacao, divida))  
            correspondencia_situacao = padrao_situacao.findall(data)
            correspondencia_dividas = padrao_dividas.findall(data)
            if correspondencia_dividas:
                situacao = correspondencia_situacao[0].strip()
                for dividas_cliente in correspondencia_dividas:
                    for linha in dividas_cliente.strip().split('\n'):
                        correspondencia_linha = padrao_linha.match(linha)
                        if correspondencia_linha:
                             ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer = correspondencia_linha.groups()
                             detalhes_divida.append([ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer])
                        # else:
                        #     detalhes_divida.append([ano or None, mes or None, tributo or None, valor_atual or None, juros or None, multa or None, total or None, vencidas or None, a_vencer or None])
                divida.append((situacao, detalhes_divida))
            dividas.append((divida))   
            # for dividas_cliente in correspondencia_dividas:
            # divida = []  # Cria uma nova instância de divida para cada dividas_cliente
            #     for linha in dividas_cliente.strip().split('\n'):
            #         correspondencia_linha = padrao_linha.match(linha)
            #         if correspondencia_linha:
            #             # ... (código omitido)
            #             divida.append([ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer])
            #         else:
            #             divida.append([ano or None, mes or None, tributo or None, valor_atual or None, juros or None, multa or None, total or None, vencidas or None, a_vencer or None])
            #     dividas.append((situacao, divida))  # Adiciona a instância de divida à lista de dividas
            imoveis.append((origem, inscricao, matricula, endereco, dividas))

# Depuração de de resultados.
for i, (origem, inscricao, matricula, endereco, dividas) in enumerate(imoveis, start=1):
    print(f"{i}\nOrigem: {origem} Inscrição: {inscricao} Matrícula: {matricula} \nEndereço: {endereco} \n{dividas}\n")
    # for j, divida in enumerate(dividas, start=1):
    #     print(f"Divida {j}: ")
        
# Criar DataFrame
df = pd.DataFrame(imoveis, columns=["Origem:", "Inscrição:", "Matrícula:", "Endereço:", "Dividas:"])
print("\n", df)

#Salvando arquivo .CSV.
df.to_csv("Relatório.csv", index=False)
print("Arquivo CSV Salvo com sucesso!")

#Salvando arquivo em formato Exel.
Excel = "Relatório.xlsx"
df.to_excel(Excel, index=False)
print("Exel Salvo com sucesso!")