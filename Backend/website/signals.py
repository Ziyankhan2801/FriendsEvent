from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.conf import settings

from .models import Booking
from .utils.invoice import generate_invoice_pdf
import threading


# ======================================================
# 🔥 BACKGROUND MAIL SENDER
# ======================================================

def send_status_mail(instance):
    try:
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
https://friendsevent.onrender.com/payment/{instance.id}/

📸 After payment, please upload the payment screenshot from the link above.
✅ Once we verify the payment, your booking will be CONFIRMED.

Thanks ❤️
{settings.BUSINESS_NAME}
📍 {settings.BUSINESS_CITY}
""".strip()

            mail = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.email],
            )
            mail.send(fail_silently=True)

        # ==================================================
        # ✅ CONFIRMED MAIL
        # ==================================================
        elif instance.status == "CONFIRMED":

            pdf_path = None
            try:
                pdf_path = generate_invoice_pdf(instance)
            except:
                pdf_path = None

            # CLIENT MAIL
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

Thanks ❤️
{settings.BUSINESS_NAME}
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

            # OWNER MAIL
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

Admin Panel:
https://friendsevent.onrender.com/admin/
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

        # ==================================================
        # ✅ DENIED MAIL
        # ==================================================
        elif instance.status == "DENIED":

            subject = "❌ Booking Request Denied"

            body = f"""
Hi {instance.name},

Sorry 😔 your booking request has been denied.

📌 Booking Details:
• Event Type: {instance.event_type}
• Date: {instance.date}
• Location: {instance.location}

Thanks ❤️
{settings.BUSINESS_NAME}
""".strip()

            mail = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.email],
            )
            mail.send(fail_silently=True)

    except Exception as e:
        print("STATUS MAIL ERROR:", e)


# ======================================================
# 🔥 MAIN SIGNAL
# ======================================================

@receiver(post_save, sender=Booking)
def booking_status_mail(sender, instance, created, **kwargs):

    if created:
        return

    last_status = getattr(instance, "last_notified_status", None)

    if last_status == instance.status:
        return

    if instance.status not in ["APPROVED", "CONFIRMED", "DENIED"]:
        return

    # 🚀 RUN MAIL IN BACKGROUND (NON BLOCKING)
    threading.Thread(
        target=send_status_mail,
        args=(instance,),
        daemon=True
    ).start()

    # ✅ Mark notified status safely
    try:
        if hasattr(instance, "last_notified_status"):
            Booking.objects.filter(id=instance.id).update(
                last_notified_status=instance.status
            )
    except:
        pass
