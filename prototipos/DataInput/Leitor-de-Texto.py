from PyPDF2 import PdfReader
import re

# Abrir o arquivo PDF em binário.
with open("sample.pdf", 'rb') as file_pdf:
    reader_pdf = PdfReader(file_pdf)

    # Obtendo o número de páginas do PDF.
    num_paginas = len(reader_pdf.pages)

    # Define um padrão para extrair as informações de endereço.
    padrao_origem = re.compile(r'Inscrição:\s*(.+).*Origem:')
    padrao_inscricao = re.compile(r'Matrícula:\s*(.+).*Inscrição:')
    # padrao_origem = re.compile(r'Origem:\s*([\d.]+).*?Inscrição:')

    # Os endereços extraídos serão armazenados nesta lista.
    informacoes = []

    # Iterar pelas páginas do PDF.
    for num_pagina in range(num_paginas):
        pagina = reader_pdf.pages[num_pagina]

        # Extração do texto da página.
        text = pagina.extract_text()
        print(text)

        # Encontrar todas as correspondências para o padrão de endereço em cada página.
        correspondencia_origem = padrao_origem.findall(text, re.DOTALL)
        correspondencia_inscricao = padrao_inscricao.findall(text, re.DOTALL)

        # Processar cada correspondência.
        for origem, inscricao in zip(correspondencia_origem, correspondencia_inscricao):
            origem = origem.strip()
            inscricao = inscricao.strip()
            informacoes.append((origem, inscricao))


# Exibir os endereços extraídos.
for i, (origem, inscricao) in enumerate(informacoes,  start=1):
    print(f"{i} Origem: {origem} Inscrição: {inscricao}")