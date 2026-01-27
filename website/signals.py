from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.conf import settings

from .models import Booking
from .utils.invoice import generate_invoice_pdf


@receiver(post_save, sender=Booking)
def booking_status_mail(sender, instance, created, **kwargs):
    # ✅ Create pe mail views.py se ja raha hai
    if created:
        return

    # ✅ Safety: Field exists? (agar DB me column nahi hoga toh crash nahi hoga)
    last_status = getattr(instance, "last_notified_status", None)

    # ✅ Spam prevention: same status pe dobara mail mat bhejo
    if last_status == instance.status:
        return

    # ✅ Only status changes in these cases
    if instance.status not in ["APPROVED", "CONFIRMED", "DENIED"]:
        return

    # ✅ APPROVED MAIL (CLIENT)
    if instance.status == "APPROVED":
        subject = "🎉 Booking Approved ✅ - Advance Payment Required"

        body = f"""
Hi {instance.name} 👋,

✅ Good News! Your booking has been APPROVED 🎉

📌 Booking Details:
• Event Type: {instance.event_type}
• Date: {instance.date}
• Location: {instance.location}
• Total Budget: ₹{instance.amount}
• Advance Amount: ₹{instance.advance_amount}

💳 Payment Method: UPI / PhonePe / GooglePay
📌 UPI ID: {settings.UPI_ID}

🔗 Payment Link (Upload Screenshot Here):
http://127.0.0.1:8000/payment/{instance.id}/

📸 After payment, please upload the payment screenshot from the link above.
✅ Once we verify the payment, your booking will be CONFIRMED.

If you need any help, reply to this email or call us 📞

Thanks ❤️
{settings.BUSINESS_NAME}
📍 {settings.BUSINESS_CITY}
""".strip()

        try:
            mail = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.email],
            )
            mail.send(fail_silently=True)
        except:
            pass

    # ✅ CONFIRMED MAIL (CLIENT + OWNER with invoice + screenshot)
    elif instance.status == "CONFIRMED":
        pdf_path = None
        try:
            pdf_path = generate_invoice_pdf(instance)
        except:
            pdf_path = None

        # ✅ CLIENT CONFIRMATION MAIL + INVOICE
        try:
            client_body = f"""
Hi {instance.name} 👋,

🎉 Congratulations! Your booking is now CONFIRMED ✅

📌 Booking Details:
• Event Type: {instance.event_type}
• Date: {instance.date}
• Location: {instance.location}
• Total Amount: ₹{instance.amount}
• Advance Paid: ₹{instance.advance_amount}

✅ Your invoice is attached in this email.

Thanks for choosing {settings.BUSINESS_NAME} ❤️
""".strip()

            client_mail = EmailMessage(
                subject="🎉 Booking Confirmed ✅ (Invoice Attached)",
                body=client_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.email],
            )

            if pdf_path:
                client_mail.attach_file(pdf_path)

            client_mail.send(fail_silently=True)
        except:
            pass

        # ✅ OWNER CONFIRMATION MAIL + INVOICE + SCREENSHOT
        try:
            owner_body = f"""
Hello Owner ✅,

🎉 Booking CONFIRMED ✅

📌 Booking Details:
• Booking ID: {instance.id}
• Name: {instance.name}
• Phone: {instance.phone}
• Email: {instance.email}
• Event Type: {instance.event_type}
• Date: {instance.date}
• Location: {instance.location}
• Total Amount: ₹{instance.amount}
• Advance Paid: ₹{instance.advance_amount}

✅ Invoice & Payment Screenshot attached.
Admin Panel: http://127.0.0.1:8000/admin/
""".strip()

            owner_mail = EmailMessage(
                subject=f"✅ Booking Confirmed - Booking #{instance.id}",
                body=owner_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.OWNER_EMAIL],
            )

            if pdf_path:
                owner_mail.attach_file(pdf_path)

            if instance.payment_screenshot and hasattr(instance.payment_screenshot, "path"):
                owner_mail.attach_file(instance.payment_screenshot.path)

            owner_mail.send(fail_silently=True)
        except:
            pass

    # ✅ DENIED MAIL (CLIENT)
    elif instance.status == "DENIED":
        subject = "❌ Booking Request Denied"
        body = f"""
Hi {instance.name},

Sorry 😔 your booking request has been denied.

📌 Booking Details:
• Event Type: {instance.event_type}
• Date: {instance.date}
• Location: {instance.location}

You can try booking again with another date.
Thanks ❤️
{settings.BUSINESS_NAME}
""".strip()

        try:
            mail = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.email],
            )
            mail.send(fail_silently=True)
        except:
            pass

    # ✅ Mark notified status (but save recursion se bachne ke liye)
    try:
        if hasattr(instance, "last_notified_status"):
            Booking.objects.filter(id=instance.id).update(last_notified_status=instance.status)
    except:
        pass
