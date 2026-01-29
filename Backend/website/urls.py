from django.urls import path
from .views import api_booking, api_gallery, payment_page, download_invoice

urlpatterns = [
    path("api/booking/", api_booking),
    path("api/gallery/", api_gallery),
    path("payment/<int:booking_id>/", payment_page, name="payment"),
    path("invoice/<int:booking_id>/", download_invoice),
]
