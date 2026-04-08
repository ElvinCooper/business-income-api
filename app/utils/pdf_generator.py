from io import BytesIO

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def generar_recibo_termico(datos: dict) -> BytesIO:
    buffer = BytesIO()

    width = 70 * mm
    height = 150 * mm

    c = canvas.Canvas(buffer, pagesize=(width, height))

    y = height - 15

    # -------- HEADER --------
    c.setFont("Courier-Bold", 10)
    c.drawCentredString(width / 2, y, datos.get("empresa", "EMPRESA"))

    y -= 10
    c.setFont("Courier", 8)
    if datos.get("direccion"):
        c.drawCentredString(width / 2, y, datos["direccion"])

    y -= 10
    if datos.get("telefono"):
        c.drawCentredString(width / 2, y, f"Tel: {datos['telefono']}")

    # -------- LINE --------
    y -= 8
    c.drawString(5, y, "-" * 42)

    # -------- TIPO TRANSACCION --------
    y -= 12
    c.setFont("Courier-Bold", 10)
    c.drawCentredString(width / 2, y, datos.get("concepto", "PAGO"))

    # -------- FECHA + TIPO --------
    y -= 12
    c.setFont("Courier", 9)
    c.drawCentredString(width / 2, y, datos["fecha"])

    # -------- METODO PAGO --------
    y -= 12
    c.setFont("Courier-Bold", 9)
    c.drawCentredString(width / 2, y, datos.get("metodo_pago", "EFECTIVO"))

    # -------- LINE --------
    y -= 10
    c.setFont("Courier", 8)
    c.drawString(5, y, "-" * 42)

    # -------- CODIGO --------
    y -= 12
    c.setFont("Courier", 9)
    c.drawString(5, y, f"Codigo.....: {datos['nro_recibo']}")

    # -------- CLIENTE --------
    y -= 12
    cliente = datos["cliente"]
    if len(cliente) > 28:
        cliente = cliente[:26] + ".."
    c.drawString(5, y, f"Cliente....: {cliente}")

    # -------- TITULO --------
    y -= 18
    c.setFont("Courier-Bold", 10)
    c.drawCentredString(width / 2, y, "DESCRIPCION DE PAGO")

    # -------- MONTO --------
    y -= 18
    c.setFont("Courier", 10)
    c.drawString(5, y, "Valor Pagado")
    c.drawRightString(width - 5, y, f"{datos['monto']:,.2f}")

    # -------- PROXIMO PAGO --------
    if datos.get("proximo_pago"):
        y -= 15
        c.setFont("Courier-Bold", 9)
        c.drawCentredString(width / 2, y, "Proximo Pago")

        y -= 12
        c.setFont("Courier", 9)
        c.drawCentredString(width / 2, y, datos["proximo_pago"])

    # -------- USUARIO --------
    if datos.get("usuario"):
        y -= 10
        c.setFont("Courier", 8)
        c.drawString(5, y, "-" * 42)

        y -= 10
        c.setFont("Courier", 9)
        c.drawCentredString(width / 2, y, datos["usuario"])

    # -------- FOOTER --------
    y -= 20
    c.setFont("Courier", 8)
    c.drawCentredString(width / 2, y, "Gracias por su pago")

    y -= 10
    c.drawCentredString(width / 2, y, "Para reclamacion Presentar Ticket")

    # y -= 10
    # c.setFont("Courier-Bold", 8)
    # c.drawCentredString(width / 2, y, "ORIGINAL - CLIENTE")

    c.save()
    buffer.seek(0)
    return buffer


def generar_reporte_ventas_termico(datos: dict) -> BytesIO:
    buffer = BytesIO()

    width = 70 * mm
    height = 180 * mm

    c = canvas.Canvas(buffer, pagesize=(width, height))

    y = height - 10
    page_number = 1

    def linea():
        nonlocal y
        y -= 5
        c.setFont("Courier", 8)
        c.drawString(5, y, "-" * 42)

    def espacio(px=8):
        nonlocal y
        y -= px

    def check_page_overflow(min_y=20):
        nonlocal y, page_number
        if y < min_y:
            c.showPage()
            y = height - 10
            page_number += 1
            c.setFont("Courier", 8)
            c.drawString(5, y, f"Pag. {page_number} de X")

    def texto_centrado(txt, size=9, bold=False):
        nonlocal y
        font = "Courier-Bold" if bold else "Courier"
        c.setFont(font, size)
        c.drawCentredString(width / 2, y, txt)

    def texto_izq_der(izq, der, size=9, bold=False, max_izq=25):
        nonlocal y
        font = "Courier-Bold" if bold else "Courier"
        c.setFont(font, size)

        if len(izq) > max_izq:
            izq = izq[: max_izq - 2] + ".."

        c.drawString(5, y, izq)
        c.drawRightString(width - 5, y, der)

    # -------- HEADER --------
    texto_centrado(datos["empresa"], 10, True)
    espacio(8)

    texto_centrado(datos["direccion"], 8)
    espacio(8)

    texto_centrado(f"Telefono(s): {datos['telefono']}", 8)
    espacio(8)

    if datos.get("rnc"):
        texto_centrado(f"RNC : {datos['rnc']}", 8)
        espacio(10)

    texto_centrado(f"Desde {datos['desde']} Hasta {datos['hasta']}", 8)
    espacio(8)

    texto_centrado(datos["fecha_impresion"], 8)
    espacio(8)

    texto_centrado(f"Impreso por : {datos['usuario']}", 8)

    linea()
    linea()

    # -------- PAG --------
    espacio(6)
    c.setFont("Courier", 8)
    c.drawString(5, y, "Pag. 1 de 1")

    # -------- TITULO --------
    espacio(10)
    texto_centrado("RESUMEN VENDIDO POR FECHA", 9, True)

    # -------- TABLA --------
    espacio(6)
    linea()

    espacio(6)
    texto_izq_der("DESCRIPCION", "Valor", 9, True)

    espacio(6)
    linea()

    # -------- ITEMS (más compacto) --------
    for item in datos["items"]:
        check_page_overflow(30)
        espacio(10)
        texto_izq_der(item["descripcion"], f"{item['valor']:,.2f}")

    # -------- TOTAL --------
    espacio(10)
    linea()

    espacio(10)
    texto_izq_der("Total Gral :", f"{datos['total']:,.2f}", 10, True)

    espacio(10)
    linea()

    # -------- RESUMEN PAGOS --------
    espacio(8)
    texto_centrado("RESUMEN DE PAGOS", 9, True)

    espacio(6)
    linea()

    for metodo in datos["pagos"]:
        check_page_overflow(20)
        espacio(10)
        metodo_limpio = metodo["tipo"].strip()
        texto_izq_der(metodo_limpio, f"{metodo['valor']:,.2f}")

    espacio(6)
    linea()

    c.save()
    buffer.seek(0)
    return buffer
