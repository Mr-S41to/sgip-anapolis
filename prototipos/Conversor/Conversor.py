import tabula

file = "data.pdf"

pdfData = tabula.read_pdf(file,pages="all")

output = tabula.convert_into(file, "resultados.csv", output_format="csv", pages=[1,2])

print(output)