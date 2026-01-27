from django.db import models

class GalleryImage(models.Model):
    title = models.CharField(max_length=120, blank=True)
    image = models.ImageField(upload_to="gallery/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else f"Gallery Image {self.id}"


class Booking(models.Model):
    STATUS_CHOICES = [
    ("PENDING", "Pending"),
    ("APPROVED", "Approved (Payment Pending)"),
    ("PAID", "Paid (Waiting Admin Confirmation)"),
    ("CONFIRMED", "Confirmed ✅"),
    ("DENIED", "Denied"),
]


    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    event_type = models.CharField(max_length=50)
    date = models.DateField()
    location = models.CharField(max_length=250)

    amount = models.IntegerField(default=0)
    message = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    admin_note = models.CharField(max_length=200, blank=True, null=True)

    # ✅ Payment fields
    advance_amount = models.IntegerField(default=0)
    payment_screenshot = models.ImageField(upload_to="payments/", blank=True, null=True)

    # ✅ Prevent duplicate mails (spam control)
    last_notified_status = models.CharField(max_length=20, blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # ✅ Safety: amount negative na ho
        if self.amount < 0:
            self.amount = 0

        # ✅ Auto calculate advance 30% (only if advance not manually set)
        if self.amount > 0 and self.advance_amount == 0:
            self.advance_amount = int(self.amount * 0.30)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.event_type} ({self.status})"
