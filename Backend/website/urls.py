from django.urls import path
from . import views

urlpatterns = [
    # APIs
    path("api/booking/", views.api_booking),
    path("api/gallery/", views.api_gallery),

    # Backend-only pages
    path("payment/<int:booking_id>/", views.payment_page, name="payment_page"),
    path("invoice/<int:booking_id>/", views.download_invoice, name="download_invoice"),
]
