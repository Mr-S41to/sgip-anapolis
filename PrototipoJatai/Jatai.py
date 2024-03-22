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
    text = re.sub(r"PREFEITURA\sMUNICIPAL\sDE\sJATAÍ", "\n", text, flags=re.MULTILINE)
    text = re.sub(r"Rua\sItarumã,.*$", "\n", text, flags=re.MULTILINE)
    text = re.sub(r"\sGO,(.+?)PE", "\n", text, flags=re.MULTILINE)
    text = re.sub(r"ADC:(.+?)\n\n", "----------", text, flags=re.DOTALL)
    # text = re.sub(r"(\d+)(?:\n\n)", "----------", text, flags=re.DOTALL)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(
        r"EXTRATO\sDE\sDÉBITO", "\nEXTRATO DE DÉBITO", text, flags=re.MULTILINE
    )
    print("Texto formatado:\n", text)

    padrao_data = re.compile(r"EXTRATO DE DÉBITO(.+?)----------", re.DOTALL)
    correspondencia_data = padrao_data

    ocorrencias_dividas = correspondencia_data.findall(text)
   
    i = 0
    for ocorrencia_divida in ocorrencias_dividas: 
        i += 1
        print(f"\n{i} - Dívida encontrada.")

        # padrao_inscricao = re.compile(r"Residencial\s(.+?)\n", re.DOTALL)
        # correspondencia_incricao = padrao_inscricao.search(ocorrencia_divida)

        # if correspondencia_incricao:
        #     inscricao = correspondencia_incricao.group(1)
        #     print("Número de inscrição:", inscricao)
        # else:
        #     inscricao = None
        #     print("Número de inscrição não encontrado.")

        padrao_inscricao_cci = re.compile(r"Inscrição:\s(\d+)CCI", re.DOTALL)
        correspondencia_incricao_cci = padrao_inscricao_cci.search(ocorrencia_divida)

        if correspondencia_incricao_cci:
            inscricao_cci = correspondencia_incricao_cci.group(1)
            print("Número de inscrição CCI:", inscricao_cci)
        else:
            inscricao_cci = None
            print("Número de inscrição CCI não encontrado.")

        padrao_local = re.compile(r"Imóvel\n(.+?),", re.DOTALL)
        correspondencia_local = padrao_local.search(ocorrencia_divida)

        if correspondencia_local:
            local = correspondencia_local.group(1)
            print("Local:", local)
        else:
            local = None
            print("Local não encontrado.")

        padrao_quadra = re.compile(r"QD\.:\s+(\d+),", re.DOTALL)
        correspondencia_quadra = padrao_quadra.search(ocorrencia_divida)

        if correspondencia_quadra:
            quadra = correspondencia_quadra.group(1)
            print("Número da quadra:", quadra)
        else:
            quadra = None
            print("Número da quadra não encontrado.")

        padrao_lote = re.compile(r"Lt\.:\s+(\d+),", re.DOTALL)
        correspondencia_lote = padrao_lote.search(ocorrencia_divida)

        if correspondencia_lote:
            lote = correspondencia_lote.group(1)
            print("Número do lote:", lote)
        else:
            lote = None
            print("Número do lote não encontrado.")

        padrao_bairro = re.compile(r"BAIRRO:\s(.+?),", re.DOTALL)
        correspondencia_bairro = padrao_bairro.search(ocorrencia_divida)

        if correspondencia_bairro:
            bairro = correspondencia_bairro.group(1)
            print("Bairro:", bairro)
        else:
            bairro = None
            print("Bairro não encontrado.")

        padrao_cidade = re.compile(r"CIDADE:\s(.+?),", re.DOTALL)
        correspondencia_cidade = padrao_cidade.search(ocorrencia_divida)

        if correspondencia_cidade:
            cidade = correspondencia_cidade.group(1)
            print("Cidade:", cidade)
        else:
            cidade = None
            print("Cidade não encontrada.")
        
        data_dividas = re.findall(r'PE.*?\w\s-\s\d+', ocorrencia_divida, re.DOTALL)
        # Junte as partes correspondentes encontradas
        # data_dividas = '\n'.join(data_dividas)
        print(data_dividas)

        divida = []
        total_dividas = 0
        for linha in data_dividas:
            # Dividir a linha pelos espaços em branco
            valores = linha.split()
            
            # Atribuir os valores a variáveis
            status = valores[0]
            parcela = valores[1]
            porcentagem = valores[2]
            variavel4 = valores[3]
            multa = valores[4]
            variavel6 = valores[5]
            total = valores[6]
            valor_tributo = valores[7]
            variavel9 = valores[8]
            vencimento = valores[9]
            tributo = valores[10]
            base = valores[11]
            correcao = valores[12]
            juros = valores[13]
            debito = valores[14]
            ref = valores[15]
            desconto = valores[16]
            
            # Exibir os valores
            print(f"\nVariáveis: Débito: {debito}, Tributo: {tributo}, Status: {status}, Ref.: {ref}, Parcela: {parcela}, Base: {base}, Porcentagem: {porcentagem}, Juros: {juros}, Multa: {multa}, Correção: {correcao}, Valor Tributo: {valor_tributo}, Desconto: {desconto}, Total: {total}, Vencimento: {vencimento}")
            print(f"Variável 4: {variavel4}")
            print(f"Variável 6: {variavel6}")
            print(f"Variável 9: {variavel9}")


    return imoveis

PDF = "sample.pdf"
imoveis_resultados = processamento_dividas(PDF)
