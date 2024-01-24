usuarios = [
    {
        "nome": "João",
        "dividas": [
            {"status": "Pendente", "valores": ["2022", "Janeiro", "Imposto de Renda", 1000.0, 50.0, 1050.0, 500.0]},
            {"status": "Quitada", "valores": ["2023", "Fevereiro", "IPVA", 1500.0, 75.0, 1575.0, 0.0]}
        ]
    },
    {
        "nome": "Maria",
        "dividas": [
            {"status": "Pendente", "valores": ["2022", "Março", "Tributo XYZ", 1200.0, 60.0, 1260.0, 600.0]},
            {"status": "Pendente", "valores": ["2023", "Abril", "Seguro", 800.0, 40.0, 840.0, 400.0]}
        ]
    }
]

# Acessando elementos
print("Dividas", usuarios)
