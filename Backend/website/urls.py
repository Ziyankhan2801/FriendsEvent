from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("submit-booking/", views.submit_booking, name="submit_booking"),
    path("payment/<int:booking_id>/", views.payment_page, name="payment_page"),
    path("invoice/<int:booking_id>/", views.download_invoice, name="download_invoice"),
]
