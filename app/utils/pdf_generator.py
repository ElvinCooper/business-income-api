from io import BytesIO

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def generar_reporte_ventas_termico(datos: dict) -> BytesIO:
    buffer = BytesIO()

    width = 70 * mm
    height = 180 * mm

    c = canvas.Canvas(buffer, pagesize=(width, height))

    y = height - 10

    def linea():
        nonlocal y
        y -= 6
        c.setFont("Courier", 8)
        c.drawString(5, y, "-" * 42)

    def espacio(px=10):
        nonlocal y
        y -= px

    def texto_centrado(txt, size=9, bold=False):
        nonlocal y
        font = "Courier-Bold" if bold else "Courier"
        c.setFont(font, size)
        c.drawCentredString(width / 2, y, txt)

    def texto_izq_der(izq, der, size=9, bold=False):
        nonlocal y
        font = "Courier-Bold" if bold else "Courier"
        c.setFont(font, size)
        c.drawString(5, y, izq)
        c.drawRightString(width - 5, y, der)

    texto_centrado(datos["empresa"], 10, True)
    espacio(10)

    texto_centrado(datos["direccion"], 8)
    espacio(10)

    texto_centrado(f"Tel: {datos['telefono']}", 8)
    espacio(10)

    texto_centrado(f"RNC: {datos['rnc']}", 8)
    espacio(12)

    texto_centrado(f"Desde {datos['desde']} Hasta {datos['hasta']}", 8)
    espacio(10)

    texto_centrado(datos["fecha_impresion"], 8)
    espacio(10)

    texto_centrado(f"Impreso por: {datos['usuario']}", 8)

    linea()

    espacio(10)
    c.setFont("Courier", 8)
    c.drawString(5, y, "Pag. 1 de 1")

    espacio(15)
    texto_centrado("RESUMEN VENDIDO POR FECHA", 9, True)

    linea()
    espacio(10)

    texto_izq_der("DESCRIPCION", "VALOR", 9, True)

    linea()

    for item in datos["items"]:
        espacio(12)
        texto_izq_der(item["descripcion"], f"{item['valor']:,.2f}")

    linea()
    espacio(12)

    texto_izq_der("Total Gral:", f"{datos['total']:,.2f}", 10, True)

    linea()
    espacio(12)

    for metodo in datos["pagos"]:
        texto_izq_der(metodo["tipo"], f"{metodo['valor']:,.2f}")
        espacio(10)

    linea()
    espacio(12)

    texto_centrado("** FIN DEL REPORTE **", 8)

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
