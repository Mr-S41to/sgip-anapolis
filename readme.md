# Aplicação de Processamento de Extratos de Débitos Imobiliários

## Sobre

Esta aplicação tem o objetivo de fazer o processamento de extratos de débitos imobiliários emitidos por contribuintes das prefeituras de Anápolis e Jataí, realizando o cruzamento de dados para emissão de relatórios de débitos
para sistemas imobiliários por meio de upload via requisição web.

O processamento é feito utilizando a linguagem Python, com a biblioteca de ciência de dados Pandas e comunicação web pelo framework Flask.

## Instruções

1. Certifique-se de ter o Python instalado.
2. Abra o terminal em cada app (Anápolis e Jataí).
3. Instale as dependências necessárias com o comando:
    ```sh
    pip install PyPDF2 pandas flask flask-cors
    ```
4. Rode as aplicações com o comando:
    ```sh
    python nome_do_arquivo.py
    ```
    É necessário que rode os dois arquivos, de Jataí e Anápolis.
