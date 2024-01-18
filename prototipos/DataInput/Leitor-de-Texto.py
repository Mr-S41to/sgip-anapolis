from PyPDF2 import PdfReader
import tabula

#Abrir pdf em binários.
with open("sample.pdf", 'rb') as pdf_file:
    pdf_reader = PdfReader(pdf_file)

    #Obtendo numero de paginas do PFF.
    num_pages = len(pdf_reader.pages)

    #Iterar as páginas do PDF.
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]

        #Extração de texto da página.
        text = page.extract_text()
        print(text)