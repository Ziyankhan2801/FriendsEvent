from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Booking
from .utils.invoice import generate_invoice_pdf
import threading


def send_async_mail(mail):
    mail.send(fail_silently=True)


@receiver(post_save, sender=Booking)
def booking_status_mail(sender, instance, created, **kwargs):
    if created:
        return

    if instance.status not in ["APPROVED", "CONFIRMED", "DENIED"]:
        return

    # =========================
    # APPROVED
    # =========================
    if instance.status == "APPROVED":

        mail = EmailMessage(
            subject="🎉 Booking Approved ✅ - Advance Payment Required",
            body=f"""
Hi {instance.name},

Your booking has been APPROVED 🎉

Advance Amount: ₹{instance.advance_amount}

Payment Link:
https://friendsevent.onrender.com/payment/{instance.id}/
""",
            from_email=settings.EMAIL_HOST_USER,
            to=[instance.email],
        )

        threading.Thread(
            target=send_async_mail,
            args=(mail,),
            daemon=True
        ).start()

    # =========================
    # CONFIRMED
    # =========================
    elif instance.status == "CONFIRMED":

        pdf_path = generate_invoice_pdf(instance)

        mail = EmailMessage(
            subject=f"🎉 Booking Confirmed - #{instance.id}",
            body="Your booking is confirmed. Invoice attached.",
            from_email=settings.EMAIL_HOST_USER,
            to=[instance.email],
        )

        if pdf_path:
            mail.attach_file(pdf_path)

        threading.Thread(
            target=send_async_mail,
            args=(mail,),
            daemon=True
        ).start()
