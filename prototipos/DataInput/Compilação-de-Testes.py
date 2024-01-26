from PyPDF2 import PdfReader
import re
import pandas as pd

def extrair_dados(text):
    padrao_origem = re.compile(r'Inscrição:\s*(.+?)\s*Origem:')
    padrao_inscricao = re.compile(r'Matrícula:\s*(.+?)\s*Inscrição:')
    padrao_matricula = re.compile(r'Matrícula:\s*(\d{3}\.\d{3}\.\d{4}\.\d{3})')
    padrao_endereco = re.compile(r'Endereço:\s*(.+?)\s*(?=\d{3}\.\d{3}\.\d{4}\.\d{3}\s*Matrícula:)')
    padrao_data = re.compile(r'Origem:(.*?)Endereço:', re.DOTALL)
    padrao_dividas = re.compile(r'Situação:\s*(.+?)\n\n', re.DOTALL)
    padrao_situacao = re.compile(r'\n*(.+?)\s*Situação:')
    padrao_linha = re.compile(r'(\d{4}) (\d{2}) (.*?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?) (\d+) (\d+)')

    imoveis = []

    correspondencia_origem = padrao_origem.findall(text)
    correspondencia_inscricao = padrao_inscricao.findall(text)
    correspondencia_matricula = padrao_matricula.findall(text)
    correspondencia_endereco = padrao_endereco.findall(text)

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

        correspondencia_data = padrao_data.search(text)

        if correspondencia_data:
            data = correspondencia_data.group(1).strip()
        else:
            data = "Padrão de dados em 'data' não encontrado."

        data = re.sub(r'\.(\s*\.)+', '', data)
        data = re.sub(r'ANO MÊS TRIBUTO VL. ATUAL. JUROS MULTA TOTAL VENCIDAS / A VENCER', '', data)
        data = re.sub(r'^.*TOTAL:$', '', data, flags=re.MULTILINE)
        data = re.sub(r'^TOTAL ORIGEM:.*$', '', data, flags=re.MULTILINE)

        situacao = None
        dividas = []

        correspondencia_situacao = padrao_situacao.findall(data)
        correspondencia_dividas = padrao_dividas.findall(data)

        if correspondencia_situacao and correspondencia_dividas:
            situacao = correspondencia_situacao[0].strip()

            for divida_cliente in correspondencia_dividas:
                detalhes_divida = []
                for linha in divida_cliente.strip().split('\n'):
                    correspondencia_linha = padrao_linha.match(linha)
                    if correspondencia_linha:
                        ano, mes, tributo, valor_atual, juros, multa, total, vencidas, a_vencer = correspondencia_linha.groups()
                        detalhes_divida.append({
                            "Ano": ano,
                            "Mês": mes,
                            "Tributo": tributo,
                            "Valor Atual": valor_atual,
                            "Juros": juros,
                            "Multa": multa,
                            "Total": total,
                            "Vencidas": vencidas,
                            "A Vencer": a_vencer
                        })

                dividas.append({
                    "Situação": situacao,
                    "Detalhes": detalhes_divida
                })

        imoveis.append({
            "Origem": origem,
            "Inscrição": inscricao,
            "Matrícula": matricula,
            "Endereço": endereco,
            "Dívidas": dividas
        })

    return imoveis

def main():
    with open("sample.pdf", 'rb') as file_pdf:
        reader_pdf = PdfReader(file_pdf)
        num_paginas = len(reader_pdf.pages)

        imoveis_totais = []

        for num_pagina in range(num_paginas):
            pagina = reader_pdf.pages[num_pagina]
            text = pagina.extract_text()

            imoveis_pagina = extrair_dados(text)
            imoveis_totais.extend(imoveis_pagina)

        for i, imovel in enumerate(imoveis_totais, start=1):
            print(f"{i}\nOrigem: {imovel['Origem']} Inscrição: {imovel['Inscrição']} Matrícula: {imovel['Matrícula']} \nEndereço: {imovel['Endereço']}")
            for j, divida in enumerate(imovel['Dívidas'], start=1):
                print(f"  Dívida {j}: Situação: {divida['Situação']}")
                for k, detalhe in enumerate(divida['Detalhes'], start=1):
                    print(f"    Detalhe {k}: {detalhe}")

        df = pd.DataFrame(imoveis_totais)
        df.to_csv("Relatório.csv", index=False)
        df.to_excel("Relatório.xlsx", index=False)

if __name__ == "__main__":
    main()
