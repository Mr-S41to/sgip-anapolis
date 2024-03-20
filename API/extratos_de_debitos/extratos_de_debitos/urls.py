from django.urls import path
from app_extratos import views

urlpatterns = [
    # rota, view, nome de referencia.
    path("processar-pdf", views.processar_pdf, name="Processamento Simplificado - Anápolis"),
]
