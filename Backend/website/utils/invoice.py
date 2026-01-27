import os
from datetime import datetime
from io import BytesIO

from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

import qrcode


def generate_invoice_pdf(booking):
    # ✅ ensure folders exist
    invoices_dir = os.path.join(settings.MEDIA_ROOT, "invoices")
    os.makedirs(invoices_dir, exist_ok=True)

    filename = f"invoice_{booking.id}.pdf"
    file_path = os.path.join(invoices_dir, filename)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # ==========================
    # Helpers
    # ==========================
    def draw_line(y, thickness=1):
        c.setLineWidth(thickness)
        c.setStrokeColor(colors.lightgrey)
        c.line(40, y, width - 40, y)

    def draw_label_value(x, y, label, value):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, label)
        c.setFont("Helvetica", 10)
        c.drawString(x + 95, y, str(value))

    # ==========================
    # HEADER BAR
    # ==========================
    c.setFillColor(colors.HexColor("#111827"))
    c.rect(0, height - 100, width, 100, fill=1, stroke=0)

    # ✅ Logo
    try:
        logo_path = getattr(settings, "BUSINESS_LOGO", None)

        # If relative path, join with BASE_DIR
        if logo_path and not os.path.isabs(str(logo_path)):
            logo_path = os.path.join(settings.BASE_DIR, str(logo_path))

        if logo_path and os.path.exists(str(logo_path)):
            c.drawImage(str(logo_path), 40, height - 85, width=55, height=55, mask="auto")
    except:
        pass

    # ✅ Business info
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(110, height - 45, getattr(settings, "BUSINESS_NAME", "Friends Events Decorative"))

    c.setFont("Helvetica", 10)
    c.drawString(110, height - 65, f"{getattr(settings, 'BUSINESS_CITY', 'Chopda, Maharashtra')}")
    c.drawString(110, height - 82, f"Phone: {getattr(settings, 'BUSINESS_PHONE', '+91XXXXXXXXXX')}")

    # ✅ Invoice Title Right
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(width - 40, height - 50, "INVOICE / BILL")

    # ==========================
    # META
    # ==========================
    invoice_no = f"INV-{booking.id:05d}"
    invoice_date = datetime.now().strftime("%d-%m-%Y")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 40, height - 120, f"Invoice No: {invoice_no}")
    c.drawRightString(width - 40, height - 135, f"Invoice Date: {invoice_date}")

    draw_line(height - 145, 1)

    # ==========================
    # ✅ PAID STAMP only if CONFIRMED
    # ==========================
    if booking.status == "CONFIRMED":
        c.saveState()
        c.translate(width - 180, height - 260)
        c.rotate(20)
        c.setStrokeColor(colors.green)
        c.setLineWidth(3)
        c.setFillColor(colors.green)
        c.setFont("Helvetica-Bold", 26)
        c.drawString(0, 0, "PAID ✅")
        c.restoreState()

    # ==========================
    # Customer Box
    # ==========================
    y = height - 185
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "BILL TO (Customer Details)")
    y -= 15

    c.setStrokeColor(colors.lightgrey)
    c.rect(40, y - 80, width - 80, 80, fill=0, stroke=1)

    y -= 20
    draw_label_value(50, y, "Name:", booking.name)
    y -= 15
    draw_label_value(50, y, "Phone:", booking.phone)
    y -= 15
    draw_label_value(50, y, "Email:", booking.email)

    # ==========================
    # Event Details Table
    # ==========================
    y = height - 310
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "EVENT DETAILS")
    y -= 15

    # header row
    c.setFillColor(colors.HexColor("#E5E7EB"))
    c.rect(40, y - 20, width - 80, 22, fill=1, stroke=0)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y - 15, "Description")
    c.drawRightString(width - 50, y - 15, "Amount (₹)")

    # data row
    y -= 35
    c.setStrokeColor(colors.lightgrey)
    c.rect(40, y - 25, width - 80, 30, fill=0, stroke=1)

    c.setFont("Helvetica", 10)
    c.drawString(50, y - 15, f"{booking.event_type} Decoration Service")
    c.drawRightString(width - 50, y - 15, f"{booking.amount}")

    # extra details
    y -= 45
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"📍 Location: {booking.location}")
    y -= 15
    c.drawString(40, y, f"📅 Event Date: {booking.date}")
    y -= 15
    c.drawString(40, y, f"✅ Status: {booking.status}")

    # ==========================
    # Amount Summary Box (Smart)
    # ==========================
    y -= 30
    total = booking.amount
    advance = booking.advance_amount or 0

    # ✅ if not paid yet
    if booking.status in ["PENDING", "APPROVED"]:
        advance_text = "Advance Due:"
        advance_value = advance
        balance_text = "Balance Due:"
        balance_value = total
    else:
        advance_text = "Advance Paid:"
        advance_value = advance
        balance_text = "Balance:"
        balance_value = max(total - advance, 0)

    c.setStrokeColor(colors.lightgrey)
    c.rect(width - 260, y - 70, 220, 70, fill=0, stroke=1)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 250, y - 20, "Total Amount:")
    c.drawRightString(width - 50, y - 20, f"₹ {total}")

    c.setFont("Helvetica", 10)
    c.drawString(width - 250, y - 40, advance_text)
    c.drawRightString(width - 50, y - 40, f"₹ {advance_value}")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 250, y - 60, balance_text)
    c.drawRightString(width - 50, y - 60, f"₹ {balance_value}")

    # ==========================
    # ✅ QR Code (UPI Payment) - NO FILE SAVE ✅
    # ==========================
    y -= 120
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y + 55, "Scan to Pay (UPI QR)")

    upi_id = getattr(settings, "UPI_ID", "yourupi@okaxis")
    business_name = getattr(settings, "BUSINESS_NAME", "Friends Events")

    pay_amount = advance if booking.status in ["APPROVED", "PENDING"] else balance_value
    if pay_amount < 0:
        pay_amount = 0

    upi_link = f"upi://pay?pa={upi_id}&pn={business_name}&am={pay_amount}&cu=INR"

    try:
        qr_img = qrcode.make(upi_link)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_reader = ImageReader(qr_buffer)
        c.drawImage(qr_reader, 40, y - 10, width=120, height=120, mask="auto")

        c.setFont("Helvetica", 10)
        c.drawString(170, y + 25, f"UPI ID: {upi_id}")
        c.drawString(170, y + 10, f"Pay Amount: ₹{pay_amount}")
    except:
        c.setFont("Helvetica", 10)
        c.drawString(40, y + 20, f"UPI ID: {upi_id}")

    # ==========================
    # Footer
    # ==========================
    draw_line(80, 1)

    c.setFont("Helvetica", 9)
    c.drawString(40, 60, "✅ Thank you for choosing Friends Events Decorative!")
    c.drawString(40, 45, "Note: Advance payment is non-refundable. Balance must be cleared before event day.")

    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 40, 45, "Authorized Signature")

    c.save()
    return file_path
