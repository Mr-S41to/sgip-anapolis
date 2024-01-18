from PyPDF2 import PdfReader
import re

# Abrir o arquivo PDF em binário.
with open("sample.pdf", 'rb') as file_pdf:
    reader_pdf = PdfReader(file_pdf)

    # Obtendo o número de páginas do PDF.
    num_paginas = len(reader_pdf.pages)

    # Define um padrão para extrair as informações de endereço.
    padrao_inscricao = re.compile(r'Matrícula:\s*([\d.]+).*?Inscrição:')

    # Os endereços extraídos serão armazenados nesta lista.
    inscricoes = []

    # Iterar pelas páginas do PDF.
    for num_pagina in range(num_paginas):
        pagina = reader_pdf.pages[num_pagina]

        # Extração do texto da página.
        text = pagina.extract_text()

        # Encontrar todas as correspondências para o padrão de endereço em cada página.
        correspondencias_inscricao = padrao_inscricao.findall(text, re.DOTALL)

        # Processar cada correspondência.
        for correspondencia in correspondencias_inscricao:
            # Remover espaços em branco no início e no final.
            inscricao = correspondencia.strip()
            inscricoes.append(inscricao)

        # Exibir o texto extraído da página.
        print(text)

# Exibir os endereços extraídos.
for i, inscricao in enumerate(inscricoes, start=1):
    print(f"Inscricao {i}: {inscricao}")
