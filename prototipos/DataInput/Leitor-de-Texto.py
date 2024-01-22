from PyPDF2 import PdfReader
import re
import tabula

# Abrir o arquivo PDF em binário.
with open("sample.pdf", 'rb') as file_pdf:
    reader_pdf = PdfReader(file_pdf)

    #Obtendo o número de páginas do PDF.
    num_paginas = len(reader_pdf.pages)

    #Define um padrão para extrair as informações de endereço.
    padrao_origem = re.compile(r'Inscrição:\s*(.+?)\s*Origem:')
    padrao_inscricao = re.compile(r'Matrícula:\s*(.+?)\s*Inscrição:')
    padrao_matricula = re.compile(r'Endereço:.*?(\d{3}\.\d{3}\.\d{4}\.\d{3})\s*Matrícula:')
    padrao_endereco = re.compile(r'Endereço:\s*(.+?)\s*(?=\d{3}\.\d{3}\.\d{4}\.\d{3}\s*Matrícula:)')
    #Ajustado para excluir o nummero de matrícula.
    padrao_data = re.compile(r'Origem:(.*?)Endereço:', re.DOTALL)

    # Os endereços extraídos serão armazenados nesta lista.
    imoveis = []

    # Iterar pelas páginas do PDF.
    for num_pagina in range(num_paginas):
        pagina = reader_pdf.pages[num_pagina]

        #Extração do texto da página.
        text = pagina.extract_text()

        # Impressão de texto para depuração
        print(f"Texto da página {num_pagina + 1}:\n{text}\n")

        # Encontrar todas as correspondências para o padrão de endereço em cada página.
        correspondencia_origem = padrao_origem.findall(text)
        correspondencia_inscricao = padrao_inscricao.findall(text)
        correspondencia_matricula = padrao_matricula.findall(text)
        correspondencia_endereco = padrao_endereco.findall(text)

        # Processar cada correspondência.
        for origem, inscricao, matricula, endereco in zip(
            correspondencia_origem, 
            correspondencia_inscricao, 
            correspondencia_matricula, 
            correspondencia_endereco
        ):
            origem = origem.strip()
            inscricao = inscricao.strip()
            matricula = matricula.strip()
            endereco = endereco.strip()

            #Aplica a expressão regular para data
            correspondencia_data = padrao_data.search(text)

            #Verifica se a correspondência foi encontrada.
            if correspondencia_data:
                #Obtém a correspondência do grupo de captura.
                data = correspondencia_data.group(1).strip()
            else:
                data = "Padrão não encontrado para esta entrada."

            imoveis.append((origem, inscricao, matricula, endereco, data))
            
#Salvar arquivo.
data_miner = "Data Miner.txt"
with open(data_miner, 'w') as miner:
    for (origem, inscricao, matricula, endereco, data) in imoveis:
        linha = f"{origem} {inscricao} {matricula} {endereco} {data}\n"
        miner.write(linha)
        
# Exibir os resultados.
for i, (origem, inscricao, matricula, endereco, data) in enumerate(imoveis,  start=1):
    print(f"{i} \nOrigem: {origem} Inscrição: {inscricao} Matrícula: {matricula} \nEndereço: {endereco} Data: {data}\n")