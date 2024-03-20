from django.shortcuts import render
from django.http import HttpResponse
from .Leitor_de_Texto import processamento_dividas


def processar_pdf(request):
    if request.method == 'POST' and request.FILES['pdf_file']:
        pdf_file = request.FILES['pdf_file']

        imoveis_resultados = processamento_dividas(pdf_file)

        return HttpResponse("PDF processado com sucesso!")
    else:
        return HttpResponse("Nenhum arquivo PDF enviado.")