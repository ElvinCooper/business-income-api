from io import BytesIO

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def generar_recibo_termico(datos: dict) -> BytesIO:
    buffer = BytesIO()

    width = 70 * mm
    height = 120 * mm

    c = canvas.Canvas(buffer, pagesize=(width, height))

    y = height - 15

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width / 2, y, "BIOCAMILA")

    y -= 12
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, y, "Pagos & Servicios")

    y -= 12
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, y, f"Recibo No: {datos['nro_recibo']}")

    y -= 12
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, f"{datos['fecha']}")

    y -= 10
    c.line(5, y, width - 5, y)

    y -= 15
    c.setFont("Helvetica-Bold", 9)
    c.drawString(5, y, "CLIENTE")

    y -= 10
    c.setFont("Helvetica", 9)
    c.drawString(5, y, datos["cliente"])

    y -= 15
    c.line(5, y, width - 5, y)

    y -= 12
    c.setFont("Helvetica-Bold", 9)
    c.drawString(5, y, "DETALLE")

    y -= 12
    c.setFont("Helvetica", 9)
    c.drawString(5, y, "Monto:")
    c.drawRightString(width - 5, y, f"${datos['monto']:,.2f}")

    y -= 10
    c.drawString(5, y, "Atendido por:")
    c.drawRightString(width - 5, y, datos["atendido_por"])

    y -= 18
    c.line(5, y, width - 5, y)

    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2, y, "TOTAL PAGADO")

    y -= 18
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, f"${datos['monto']:,.2f}")

    y -= 20
    c.line(5, y, width - 5, y)

    y -= 12
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, y, "Gracias por su pago")

    y -= 10
    c.drawCentredString(width / 2, y, "Conserve este recibo")

    y -= 12
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(width / 2, y, "ORIGINAL - CLIENTE")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer


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
