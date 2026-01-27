from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.http import FileResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import quote
import json

from .models import GalleryImage, Booking
from .utils.invoice import generate_invoice_pdf


# ======================================================
# HOME (only for Django admin / testing, optional)
# ======================================================
def home(request):
    images = GalleryImage.objects.order_by("-uploaded_at")[:8]
    gallery_list = [{"image": img.image.url} for img in images]

    return render(request, "index.html", {
        "images": images,
        "gallery_list": gallery_list
    })


# ======================================================
# 🔥 BOOKING API (Netlify → Render)
# ======================================================
@csrf_exempt
def api_booking(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)

        booking = Booking.objects.create(
            name=data.get("name"),
            phone=data.get("phone"),
            email=data.get("email"),
            event_type=data.get("event_type"),
            date=data.get("date"),
            location=data.get("location"),
            amount=int(data.get("amount", 0)),
            message=data.get("message", ""),
            status="PENDING"
        )

        # ✅ OWNER MAIL
        try:
            send_mail(
                "📩 New Booking Request (PENDING)",
                f"""
New booking received ✅

Name: {booking.name}
Phone: {booking.phone}
Email: {booking.email}
Event: {booking.event_type}
Date: {booking.date}
Location: {booking.location}
Budget: ₹{booking.amount}

Status: PENDING
""",
                settings.EMAIL_HOST_USER,
                [settings.OWNER_EMAIL],
                fail_silently=True
            )
        except:
            pass

        # ✅ CLIENT MAIL
        try:
            send_mail(
                "✅ Booking Received - Friends Events",
                f"""
Hi {booking.name},

Your booking request has been received successfully ✅
Current Status: PENDING

We will contact you soon.

Thanks ❤️
{settings.BUSINESS_NAME}
""",
                settings.EMAIL_HOST_USER,
                [booking.email],
                fail_silently=True
            )
        except:
            pass

        return JsonResponse({
            "success": True,
            "booking_id": booking.id
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


# ======================================================
# 💳 PAYMENT PAGE
# ======================================================
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # ❌ Not approved yet
    if booking.status not in ["APPROVED", "PAID"]:
        return render(request, "payment_wait.html", {"booking": booking})

    # ✅ Already paid
    if booking.status == "PAID":
        return render(request, "payment_done.html", {"booking": booking})

    upi_id = settings.UPI_ID
    business_name = settings.BUSINESS_NAME

    pay_amount = booking.advance_amount if booking.advance_amount > 0 else booking.amount

    upi_link = (
        f"upi://pay?pa={quote(upi_id)}"
        f"&pn={quote(business_name)}"
        f"&am={pay_amount}"
        f"&cu=INR"
        f"&tn={quote(f'Booking#{booking.id} Advance Payment')}"
    )

    if request.method == "POST":
        if "payment_screenshot" not in request.FILES:
            messages.error(request, "❌ Please upload payment screenshot")
            return redirect("payment_page", booking_id=booking.id)

        booking.payment_screenshot = request.FILES["payment_screenshot"]
        booking.status = "PAID"
        booking.save()

        # ✅ OWNER MAIL
        try:
            owner_mail = EmailMessage(
                subject=f"✅ Payment Screenshot Uploaded - Booking #{booking.id}",
                body=f"""
Payment screenshot uploaded ✅

Name: {booking.name}
Phone: {booking.phone}
Email: {booking.email}
Event: {booking.event_type}
Date: {booking.date}
Location: {booking.location}

Advance Paid: ₹{booking.advance_amount}
Status: PAID (Waiting confirmation)
""",
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.OWNER_EMAIL]
            )

            if booking.payment_screenshot:
                owner_mail.attach_file(booking.payment_screenshot.path)

            owner_mail.send(fail_silently=True)
        except:
            pass

        # ✅ CLIENT MAIL
        try:
            send_mail(
                "✅ Payment Uploaded - Friends Events",
                f"""
Hi {booking.name},

Your payment screenshot has been received ✅
Please wait while admin confirms your booking.

Thanks ❤️
{settings.BUSINESS_NAME}
""",
                settings.EMAIL_HOST_USER,
                [booking.email],
                fail_silently=True
            )
        except:
            pass

        messages.success(request, "✅ Payment uploaded successfully!")
        return redirect("payment_page", booking_id=booking.id)

    return render(request, "payment.html", {
        "booking": booking,
        "upi_id": upi_id,
        "business_name": business_name,
        "upi_link": upi_link,
        "pay_amount": pay_amount
    })


# ======================================================
# 📄 DOWNLOAD INVOICE
# ======================================================
def download_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    pdf_path = generate_invoice_pdf(booking)

    return FileResponse(
        open(pdf_path, "rb"),
        as_attachment=True,
        filename=f"invoice_{booking.id}.pdf"
    )