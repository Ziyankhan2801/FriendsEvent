from django.contrib import admin
from django.conf import settings

from .models import Booking, GalleryImage


@admin.register(GalleryImage)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "uploaded_at")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "event_type", "date", "amount", "status")
    list_filter = ("status", "event_type")
    search_fields = ("name", "phone", "email")

    actions = ["approve_booking", "confirm_booking"]

    def approve_booking(self, request, queryset):
        """
        Only update status to APPROVED
        Mail automatically signals.py se jayega
        """
        updated = 0
        for booking in queryset:
            if booking.status == "PENDING":
                # advance auto calculate already model save me bhi ho raha
                booking.status = "APPROVED"
                booking.save()
                updated += 1

        self.message_user(request, f"✅ {updated} booking(s) APPROVED. Payment mail client ko signals.py se gaya.")

    approve_booking.short_description = "✅ Approve Booking (Send Payment Mail via Signals)"

    def confirm_booking(self, request, queryset):
        """
        Owner manual confirm karega (after verifying screenshot)
        CONFIRMED mail dono ko signals.py se jayega (invoice + screenshot attach)
        """
        updated = 0
        for booking in queryset:
            if booking.status == "PAID":
                booking.status = "CONFIRMED"
                booking.save()
                updated += 1

        self.message_user(request, f"✅ {updated} booking(s) CONFIRMED. Confirm mail signals.py se gaya.")

    confirm_booking.short_description = "✅ Confirm Booking (After Payment Verified)"
