from PyPDF2 import PdfReader
import re
import pandas as pd

# Open the PDF file in binary mode.
with open("sample.pdf", 'rb') as file_pdf:
    reader_pdf = PdfReader(file_pdf)

    # Get the number of pages in the PDF.
    num_paginas = len(reader_pdf.pages)

    # Define a pattern to extract address information.
    padrao_origem = re.compile(r'Inscrição:\s*(.+?)\s*Origem:')
    padrao_inscricao = re.compile(r'Matrícula:\s*(.+?)\s*Inscrição:')
    padrao_matricula = re.compile(r'Endereço:.*?(\d{3}\.\d{3}\.\d{4}\.\d{3})\s*Matrícula:' or r'Endereço:\s*(.+?)\s*Matrícula:')
    padrao_endereco = re.compile(r'Endereço:\s*(.+?)\s*(?=\d{3}\.\d{3}\.\d{4}\.\d{3}\s*Matrícula:)')
    # Adjusted to exclude the matricula number.
    padrao_data = re.compile(r'Origem:(.*?)Endereço:', re.DOTALL)
    padrao_dividas = re.compile(r'Situação:\s*(.+?)\sANO' or r'Situação:\s*(.+?)\sTOTAL ORIGEM:', re.DOTALL)
    padrao_situacao = re.compile(r'\n*(.+?)\s*Situação:')

    # The extracted objects will be stored in this list.
    imoveis = []

    # Iterate through the pages of the PDF.
    for num_pagina in range(num_paginas):
        pagina = reader_pdf.pages[num_pagina]

        # Extract text from the page.
        text = pagina.extract_text()

        # Print text for debugging.
        print(f"Texto da página {num_pagina + 1}:\n{text}\n")

        # Find all matches for the address pattern on each page.
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
            matricula = matricula.strip()
            endereco = endereco.strip()

            # Apply the regular expression for date.
            correspondencia_data = padrao_data.search(text)
            # Verify if the match was found.
            if correspondencia_data:
                # Get the match from the capture group.
                data = correspondencia_data.group(1).strip()
            else:
                data = "Padrão não encontrado para esta entrada."
            data = re.sub(r'\.(\s*\.)+', '', data)
            data = re.sub(r'ANO MÊS TRIBUTO VL. ATUAL. JUROS MULTA TOTAL VENCIDAS / A VENCER', '', data)
            data = re.sub(r'\bTOTAL:\s*$', '', data, flags=re.MULTILINE)
            data = re.sub(r'^TOTAL ORIGEM:.*$', '', data, flags=re.MULTILINE)

            dividas = []
            if "Situação:" in data:
                correspondencia_situacao = padrao_situacao.findall(data)
                for situacao in correspondencia_situacao:
                    situacao.strip()
                    divida = [situacao]
                dividas.append(divida) 
                               
            imoveis.append((origem, inscricao, matricula, endereco, data, dividas))

# Display the results.
for i, (origem, inscricao, matricula, endereco, data, dividas) in enumerate(imoveis, start=1):
    print(f"{i} \nOrigem: {origem} Inscrição: {inscricao} Matrícula: {matricula} \nEndereço: {endereco} \n\nDados Brutos: {data} \nDividas: {dividas}")

# Create a DataFrame
df = pd.DataFrame(imoveis, columns=["Origem:", "Inscrição:", "Matrícula:", "Endereço:", "Dados Brutos", "Dividas:"])

# Display the DataFrame
print("\n", df)

# Save the DataFrame as CSV
df.to_csv("Relatório.csv", index=False)

# Save the DataFrame as Excel
Excel = "Relatório.xlsx"
df.to_excel(Excel, index=False)

print("Salvo com sucesso!")