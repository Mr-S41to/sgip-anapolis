from PyPDF2 import PdfReader
import re
import pandas as pd

# Abrir o arquivo PDF em modo binário.
with open("sample.pdf", 'rb') as file_pdf:
    reader_pdf = PdfReader(file_pdf)
    num_paginas = len(reader_pdf.pages)

    # Os dados serão armazenados nesta lista.
    imoveis = []

    # Iterate through the pages of the PDF.
    for num_pagina in range(num_paginas):
        pagina = reader_pdf.pages[num_pagina]
        text = pagina.extract_text()

        # Debugging de leitura de arquivo.
        print(f"Texto da página {num_pagina + 1}:\n{text}\n")

        # Correspondência de Headers.
        padrao_origem = re.compile(r'Inscrição:\s*(.+?)\s*Origem:')
        padrao_inscricao = re.compile(r'Matrícula:\s*(.+?)\s*Inscrição:')
        padrao_matricula = re.compile(r'Endereço:.*?(\d{3}\.\d{3}\.\d{4}\.\d{3})\s*Matrícula:')
        padrao_endereco = re.compile(r'Endereço:\s*(.+?)\s*(?=\d{3}\.\d{3}\.\d{4}\.\d{3}\s*Matrícula:)')

        correspondencia_origem = padrao_origem.findall(text)
        correspondencia_inscricao = padrao_inscricao.findall(text)
        correspondencia_matricula = padrao_matricula.findall(text)
        correspondencia_endereco = padrao_endereco.findall(text)

        # Processamento de correspondências.
        for origem, inscricao, endereco, matricula in zip(
            correspondencia_origem,
            correspondencia_inscricao,
            correspondencia_endereco,
            correspondencia_matricula
        ):
            origem = origem.strip()
            inscricao = inscricao.strip()
            matricula = matricula.strip() if correspondencia_matricula else None
            endereco = endereco.strip()

            # Obtendo correspondência de dados.
            padrao_data = re.compile(r'Origem:(.*?)Endereço:', re.DOTALL)
            data = padrao_data.search(text).group(1).strip()

            # Formatando os dados.
            data = re.sub(r'\.(\s*\.)+', '', data)
            data = re.sub(r'ANO MÊS TRIBUTO VL. ATUAL. JUROS MULTA TOTAL VENCIDAS / A VENCER', '', data)
            data = re.sub(r'^.*TOTAL:$', '', data, flags=re.MULTILINE)
            data = re.sub(r'^TOTAL ORIGEM:.*$', '', data, flags=re.MULTILINE)

            # Correspondência de dívidas e situação.
            padrao_dividas = re.compile(r'Situação:\s*(.+?)\n\n', re.DOTALL)
            padrao_situacao = re.compile(r'\n*(.+?)\s*Situação:')
            correspondencia_dividas = padrao_dividas.findall(data)
            correspondencia_situacao = padrao_situacao.findall(data)

            situacao = correspondencia_situacao[0].strip() if correspondencia_situacao else None
            dividas = []

            if correspondencia_dividas and correspondencia_situacao:
                for dividas_cliente in correspondencia_dividas:
                    divida = []
                    for linha in dividas_cliente.strip().split('\n'):
                        padrao_linha = re.compile(r'(\d{4}) (\d{2}) (.*?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d+) (\d+)')
                        correspondencia_linha = padrao_linha.match(linha)
                        if correspondencia_linha:
                            ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer = correspondencia_linha.groups()
                            divida.append({
                                "Ano": ano,
                                "Mês": mes,
                                "Tributo": tributo,
                                "Valor Atual": valor_atual,
                                "Juros": juros,
                                "Multa": multa,
                                "Vencidas": vencidas,
                                "A Vencer": a_vencer
                            })

                    dividas.append({
                        "Situação": situacao,
                        "Divida": divida
                    })

            imoveis.append({
                "Origem": origem,
                "Inscrição": inscricao,
                "Matrícula": matricula,
                "Endereço": endereco,
                "Dívidas": dividas
            })

# Depuração de resultados.
for i, imovel in enumerate(imoveis, start=1):
    origem = imovel['Origem']
    inscricao = imovel['Inscrição']
    matricula = imovel['Matrícula']
    endereco = imovel['Endereço']
    dividas = imovel['Dívidas']

    print(f"{i}\nOrigem: {origem} Inscrição: {inscricao} Matrícula: {matricula} \nEndereço: {endereco} \n{dividas}\n")

# Criar DataFrame
df = pd.DataFrame(imoveis)
df.to_csv("Relatório.csv", index=False)
df.to_excel("Relatório.xlsx", index=False)
print("Arquivos CSV e Excel salvos com sucesso!")
