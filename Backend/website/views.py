from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.http import FileResponse
from django.contrib import messages
from urllib.parse import quote

from .models import GalleryImage, Booking
from .utils.invoice import generate_invoice_pdf


def home(request):
    images = GalleryImage.objects.order_by("-uploaded_at")[:8]
    gallery_list = [{"image": img.image.url} for img in images]

    return render(request, "index.html", {
        "images": images,
        "gallery_list": gallery_list
    })


def submit_booking(request):
    if request.method == "POST":
        amount = int(request.POST.get("amount", 0))

        booking = Booking.objects.create(
            name=request.POST["name"],
            phone=request.POST["phone"],
            email=request.POST["email"],
            event_type=request.POST["eventType"],
            date=request.POST["date"],
            location=request.POST["location"],
            amount=amount,
            message=request.POST.get("message", ""),
            status="PENDING"
        )

        # ✅ OWNER MAIL (Pending)
        try:
            send_mail(
                "📩 New Booking Request (PENDING)",
                f"New booking received ✅\n\n"
                f"Name: {booking.name}\n"
                f"Phone: {booking.phone}\n"
                f"Email: {booking.email}\n"
                f"Event: {booking.event_type}\n"
                f"Date: {booking.date}\n"
                f"Location: {booking.location}\n"
                f"Budget: ₹{booking.amount}\n"
                f"Message: {booking.message}\n\n"
                f"Status: PENDING\n"
                f"Admin Panel: http://127.0.0.1:8000/admin/",
                settings.EMAIL_HOST_USER,
                [settings.OWNER_EMAIL],
                fail_silently=True
            )
        except:
            pass

        # ✅ CLIENT MAIL (Request received)
        try:
            send_mail(
                "✅ Booking Received - Friends Events Decorative",
                f"Hi {booking.name},\n\n"
                f"✅ Your booking request has been received.\n"
                f"Current Status: PENDING\n\n"
                f"We will approve soon.\n\nThanks ❤️",
                settings.EMAIL_HOST_USER,
                [booking.email],
                fail_silently=True
            )
        except:
            pass

        return render(request, "booking_success.html", {"booking": booking})

    return redirect("home")


# ✅ PAYMENT PAGE
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # ✅ Only allow payment when APPROVED
    if booking.status != "APPROVED":
        return render(request, "payment_wait.html", {"booking": booking})

    # ✅ If already paid show done page
    if booking.status == "PAID":
        return render(request, "payment_done.html", {"booking": booking})

    # ✅ UPI Payment Link (for QR generation)
    # NOTE: amount yaha advance_amount show karna best hai
    upi_id = getattr(settings, "UPI_ID", "")
    business_name = getattr(settings, "BUSINESS_NAME", "Friends Events Decorative")

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
            messages.error(request, "❌ Please upload payment screenshot!")
            return redirect("payment_page", booking_id=booking.id)

        booking.payment_screenshot = request.FILES["payment_screenshot"]
        booking.status = "PAID"  # ✅ paid upload done (admin will CONFIRM later)
        booking.save()

        # ✅ OWNER MAIL - Payment screenshot received (No confirm yet)
        try:
            owner_mail = EmailMessage(
                subject=f"✅ Payment Screenshot Uploaded - Booking #{booking.id}",
                body=f"""
Hello Owner ✅

Client has uploaded payment screenshot.

Booking Details:
Name: {booking.name}
Phone: {booking.phone}
Email: {booking.email}
Event: {booking.event_type}
Date: {booking.date}
Location: {booking.location}

Total Amount: ₹{booking.amount}
Advance Amount: ₹{booking.advance_amount}

Status: PAID (Waiting for Admin CONFIRMATION ✅)

Admin Panel:
http://127.0.0.1:8000/admin/
""",
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.OWNER_EMAIL],
            )

            # ✅ attach screenshot
            if booking.payment_screenshot and booking.payment_screenshot.path:
                owner_mail.attach_file(booking.payment_screenshot.path)

            owner_mail.send(fail_silently=True)
        except:
            pass

        # ✅ client mail (wait for confirmation)
        try:
            send_mail(
                "✅ Payment Uploaded - Waiting for Confirmation",
                f"Hi {booking.name},\n\n"
                f"✅ Your payment screenshot has been received.\n"
                f"Now please wait, admin will confirm your booking soon.\n\n"
                f"Booking ID: {booking.id}\n"
                f"Thanks ❤️",
                settings.EMAIL_HOST_USER,
                [booking.email],
                fail_silently=True
            )
        except:
            pass

        messages.success(request, "✅ Payment uploaded! Now wait for admin confirmation.")
        return redirect("payment_page", booking_id=booking.id)

    return render(request, "payment.html", {
        "booking": booking,
        "upi_id": upi_id,
        "business_name": business_name,
        "upi_link": upi_link,
        "pay_amount": pay_amount
    })


def download_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    pdf_path = generate_invoice_pdf(booking)
    return FileResponse(open(pdf_path, "rb"), as_attachment=True, filename=f"invoice_{booking.id}.pdf")
