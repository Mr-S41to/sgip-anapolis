from PyPDF2 import PdfReader
import re

def processamento_dividas(PDF):
    # Abrir pedef em Binários.
    with open(PDF, "rb") as file_pdf:
        reader_pdf = PdfReader(file_pdf)
        num_paginas = len(reader_pdf.pages)

        text = ""
        imoveis = []

        # Iterando entre paginas do PDF.
        for num_pagina in range(num_paginas):
            pagina = reader_pdf.pages[num_pagina]
            # Extração do texto das paginas
            text += pagina.extract_text()
            # Debugging de leitura de arquivo.
            print(text)
    
    text = re.sub(r"\s\d\sPágina.*$", "\n", text, flags=re.MULTILINE)
    text = re.sub(r"\s\d\d\sPágina.*$", "\n", text, flags=re.MULTILINE)
    text = re.sub(r"^\s\sImpresso.*$", "\n", text, flags=re.MULTILINE)
    text = re.sub(r"EXTRATO\sDE\sDÉBITO", "\n", text, flags=re.MULTILINE)
    text = re.sub(r"PREFEITURA\sMUNICIPAL\sDE\sJATAÍ", "\n", text, flags=re.MULTILINE)
    text = re.sub(r"Rua\sItarumã,.*$", "\n", text, flags=re.MULTILINE)
    text = re.sub(r"ADC:(.+?)\n\n", "\n", text, flags=re.DOTALL)
    text = re.sub(r"\n\n+", "\n\n", text)
    print(text)

    padrao_data = re.compile(r"\n\n(.+?)\n\n", re.DOTALL)
    correspondencia_data = padrao_data

    ocorrencias_dividas = correspondencia_data.findall(text)

    for ocorrencia_divida in ocorrencias_dividas:
        print("\n\nXXX---XXX",ocorrencia_divida)

PDF = "sample.pdf"
imoveis_resultados = processamento_dividas(PDF)