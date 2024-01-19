from PyPDF2 import PdfReader
import re
import tabula

# Abrir o arquivo PDF em binário.
with open("sample.pdf", 'rb') as file_pdf:
    reader_pdf = PdfReader(file_pdf)

    # Obtendo o número de páginas do PDF.
    num_paginas = len(reader_pdf.pages)

    # Define um padrão para extrair as informações de endereço.
    padrao_origem = re.compile(r'Inscrição:\s*(.+).*Origem:')
    padrao_inscricao = re.compile(r'Matrícula:\s*(.+).*Inscrição:')
    padrao_matricula = re.compile(r'Endereço:.*?(\d{3}\.\d{3}\.\d{4}\.\d{3})\s*Matrícula:')
    #Exemplo de padão de numero de Matrícula: 404.004.0116.000 
    # padrao_origem = re.compile(r'Origem:\s*([\d.]+).*?Inscrição:')

    # Os endereços extraídos serão armazenados nesta lista.
    imoveis = []

    # Iterar pelas páginas do PDF.
    for num_pagina in range(num_paginas):
        pagina = reader_pdf.pages[num_pagina]

        # Extração do texto da página.
        text = pagina.extract_text()
        print(text)

        # Encontrar todas as correspondências para o padrão de endereço em cada página.
        correspondencia_origem = padrao_origem.findall(text, re.DOTALL)
        correspondencia_inscricao = padrao_inscricao.findall(text, re.DOTALL)
        correspondencia_matricula = padrao_matricula.findall(text, re.DOTALL)

        # Processar cada correspondência.
        for origem, inscricao, matricula in zip(correspondencia_origem, correspondencia_inscricao, correspondencia_matricula):
            #Operador zip para combinar os valores das duas expressões regulares em uma única tupla. 
            origem = origem.strip()
            inscricao = inscricao.strip()
            matricula = matricula.strip()
            imoveis.append((origem, inscricao, matricula))

            # # Utilizar tabula para extrair tabelas da página
            # tabelas = tabula.read_pdf("sample.pdf", pages=num_pagina + 1, multiple_tables=True)

            # # Processar cada tabela encontrada
            # for tabela in tabelas:
            #     # Aqui você pode processar a tabela conforme necessário
            #     print("Tabela encontrada:")
            #     print(tabela)

# Exibir os endereços extraídos.
for i, (origem, inscricao, matricula) in enumerate(imoveis,  start=1):
    print(f"{i} Origem: {origem} Inscrição: {inscricao} Matrícula: {matricula}")