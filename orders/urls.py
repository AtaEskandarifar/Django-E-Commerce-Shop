from django.urls import path
from .views import *
from django.views.generic import TemplateView

app_name = 'orders'
urlpatterns = [
    # Checkout page
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    #order list page
    path("", OrderListView.as_view(), name="order_list"),
    # Payment redirect
    path("payment/<uuid:order_id>/", PaymentView.as_view(), name="payment"),

    # Payment verification callback
    path("verify/<uuid:order_id>/", PaymentVerifyView.as_view(), name="payment_verify"),

    # Payment result pages
    path("payment/success/<uuid:order_id>/", PaymentResultView.as_view(template_name="orders/payment_success.html"), name="payment_success"),
    path("payment/failed/<uuid:order_id>/", PaymentResultView.as_view(template_name="orders/payment_failed.html"), name="payment_failed"),
    path("<uuid:pk>/", OrderDetailView.as_view(), name="order_detail"),
]
