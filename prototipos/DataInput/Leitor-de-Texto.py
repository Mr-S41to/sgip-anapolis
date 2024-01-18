from PyPDF2 import PdfReader
import re

# Abrir o arquivo PDF em binário.
with open("sample.pdf", 'rb') as file_pdf:
    reader_pdf = PdfReader(file_pdf)
    # Obtendo o número de páginas do PDF.
    num_paginas = len(reader_pdf.pages)

    # Os imóveis extraídos serão armazenados nesta lista.
    imoveis = []

    # Define padrões para extrair as informações de endereço.
    padrao_origem = re.compile(r'Origem:\s*(.+)')
    padrao_inscricao = re.compile(r'Inscrição:\s*(.+)')
    padrao_matricula = re.compile(r'Matrícula:\s*(.+)')

    # Iterar pelas páginas do PDF.
    for num_pagina in range(num_paginas):
        pagina = reader_pdf.pages[num_pagina]

        # Extração do texto da página.
        text = pagina.extract_text()

        # Exibir o texto extraído da página.
        print(text)

        # Encontrar todas as correspondências para o padrão de endereço em cada página.
        correspondencia_origem = padrao_origem.search(text)
        correspondencia_inscricao = padrao_inscricao.search(text)
        correspondencia_matricula = padrao_matricula.search(text)

        # Processar cada correspondência.
        origem = correspondencia_origem.group(1).strip() if correspondencia_origem else None
        inscricao = correspondencia_inscricao.group(1).strip() if correspondencia_inscricao else None
        matricula = correspondencia_matricula.group(1).strip() if correspondencia_matricula else None

        # imoveis.append({origem,  inscricao, matricula})
        imoveis.append({'Origem': origem, 'Inscrição': inscricao, 'Matrícula': matricula})

# E ajuste o loop de impressão para iterar sobre os dicionários:
for i, resultado in enumerate(imoveis, start=1):
    print(f"\nConjunto de Dados {i}:")
    print(f"Origem: {resultado['Origem']}")
    print(f"Inscrição: {resultado['Inscrição']}")
    print(f"Matrícula: {resultado['Matrícula']}")

# from PyPDF2 import PdfReader
# import re

# # Abrir o arquivo PDF em binário.
# with open("sample.pdf", 'rb') as file_pdf:
#     reader_pdf = PdfReader(file_pdf)

#     # Obtendo o número de páginas do PDF.
#     num_paginas = len(reader_pdf.pages)

#     # Define um padrão para extrair as informações de endereço.
#     padrao_inscricao = re.compile(r'Matrícula:\s*([\d.]+).*?Inscrição:')

#     # Os endereços extraídos serão armazenados nesta lista.
#     inscricoes = []

#     # Iterar pelas páginas do PDF.
#     for num_pagina in range(num_paginas):
#         pagina = reader_pdf.pages[num_pagina]

#         # Extração do texto da página.
#         text = pagina.extract_text()

#         # Encontrar todas as correspondências para o padrão de endereço em cada página.
#         correspondencias_inscricao = padrao_inscricao.findall(text, re.DOTALL)

#         # Processar cada correspondência.
#         for correspondencia in correspondencias_inscricao:
#             # Remover espaços em branco no início e no final.
#             inscricao = correspondencia.strip()
#             inscricoes.append(inscricao)

#         # Exibir o texto extraído da página.
#         print(text)

# # Exibir os endereços extraídos.
# for i, inscricao in enumerate(inscricoes, start=1):
#     print(f"Inscrição {i}: {inscricao}")