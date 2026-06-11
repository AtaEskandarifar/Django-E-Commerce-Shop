import logging

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.views.generic import TemplateView, DetailView, ListView

from .forms import OrderForm
from .models import Order, OrderItem
from .zarinpal_service import initiate_payment, verify_payment, STARTPAY_URL

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Step 1: Checkout View
# --------------------------------------------------------------------------
class CheckoutView(LoginRequiredMixin, View):
    template_name = "orders/checkout.html"

    def get(self, request):
        cart = self.get_cart(request.user)
        if not cart:
            return redirect("carts:cart")

        form = OrderForm()
        subtotal = cart.total_price
        tax_amount = self.calculate_tax(subtotal)
        final_total = subtotal + tax_amount

        return render(
            request,
            self.template_name,
            {
                "cart": cart,
                "form": form,
                "tax_amount": tax_amount,
                "final_total": final_total,
            },
        )

    def post(self, request):
        cart = self.get_cart(request.user)
        if not cart:
            return redirect("carts:cart")

        existing_order = Order.objects.filter(
            user=request.user,
            payment_status=Order.PaymentStatus.WAITING,
        ).order_by("-created_at").first()

        if existing_order:
            return redirect("orders:payment", order_id=existing_order.id)

        form = OrderForm(request.POST)
        if not form.is_valid():
            subtotal = cart.total_price
            tax_amount = self.calculate_tax(subtotal)
            final_total = subtotal + tax_amount
            return render(
                request,
                self.template_name,
                {
                    "cart": cart,
                    "form": form,
                    "tax_amount": tax_amount,
                    "final_total": final_total,
                },
            )

        subtotal = cart.total_price
        tax_amount = self.calculate_tax(subtotal)
        final_total = subtotal + tax_amount

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                province=form.cleaned_data["province"],
                city=form.cleaned_data["city"],
                address=form.cleaned_data["address"],
                postal_code=form.cleaned_data["postal_code"],
                phone=form.cleaned_data["phone"],
                note=form.cleaned_data["note"],
                discount_amount=0,
            )

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_type=cart_item.product_type,
                    product_id=cart_item.product_id,
                    product_name=cart_item.product.name,
                    unit_price=cart_item.product.offer_price,
                    quantity=cart_item.quantity,
                )

        request.session["payment_amount"] = final_total
        return redirect("orders:payment", order_id=order.id)

    def get_cart(self, user):
        cart = getattr(user, "cart", None)
        if not cart or not cart.items.exists():
            return None
        return cart

    def calculate_tax(self, subtotal):
        return round(subtotal * 0.10)


# --------------------------------------------------------------------------
# Step 2: Payment Redirect
# --------------------------------------------------------------------------
class PaymentView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.payment_status == Order.PaymentStatus.PAID:
            return redirect("orders:payment_success", order_id=order.id)

        amount_toman = order.final_price
        amount_rial = int(amount_toman) * 10

        if amount_toman <= 0:
            return render(
                request,
                "orders/payment_failed.html",
                {"error": "Invalid payment amount."},
            )

        callback_url = request.build_absolute_uri(
            reverse("orders:payment_verify", args=[order.id])
        )

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order.id)

                if order.authority:
                    return redirect(STARTPAY_URL + order.authority)

                payment_url, authority = initiate_payment(
                    amount=amount_rial,
                    description=f"Order #{order.factor_code}",
                    callback_url=callback_url,
                    email=request.user.email,
                    mobile=getattr(request.user, "phone", None),
                    order_id=order.id,
                )

                order.authority = authority
                order.save(update_fields=["authority"])

        except Exception as e:
            logger.exception("Payment initiation failed for order %s", order.id)
            return render(
                request,
                "orders/payment_failed.html",
                {"error": str(e)},
            )

        return redirect(payment_url)


# --------------------------------------------------------------------------
# Step 3: Payment Verification
# --------------------------------------------------------------------------
class PaymentVerifyView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.payment_status == Order.PaymentStatus.PAID:
            return redirect("orders:payment_success", order_id=order.id)

        authority = request.GET.get("Authority")
        status = request.GET.get("Status")

        if status != "OK" or not authority:
            return self._fail(order)

        if not order.authority or authority != order.authority:
            return self._fail(order)

        amount_rial = int(order.final_price) * 10
        success, ref_id = verify_payment(amount_rial, authority)

        if not success:
            return self._fail(order)

        with transaction.atomic():
            order.refresh_from_db()

            if order.payment_status == Order.PaymentStatus.PAID:
                return redirect("orders:payment_success", order_id=order.id)

            order.payment_status = Order.PaymentStatus.PAID
            order.payment_ref_id = ref_id
            order.paid_at = timezone.now()
            order.order_status = Order.OrderStatus.PROCESSING
            order.save(
                update_fields=[
                    "payment_status",
                    "payment_ref_id",
                    "paid_at",
                    "order_status",
                ]
            )

            cart = getattr(order.user, "cart", None)
            if cart:
                cart.items.all().delete()

        return redirect("orders:payment_success", order_id=order.id)

    def _fail(self, order):
        if order.payment_status != Order.PaymentStatus.FAILED:
            order.payment_status = Order.PaymentStatus.FAILED
            order.save(update_fields=["payment_status"])

        return redirect("orders:payment_failed", order_id=order.id)


# --------------------------------------------------------------------------
# Step 4: Payment Success
# --------------------------------------------------------------------------
class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.payment_status != Order.PaymentStatus.PAID:
            return HttpResponseForbidden("Invalid access")

        return render(request, "orders/payment_success.html", {"order": order})


# --------------------------------------------------------------------------
# Step 5: Payment Failed
# --------------------------------------------------------------------------
class PaymentFailedView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return render(request, "orders/payment_failed.html", {"order": order})


# --------------------------------------------------------------------------
# Step 6: Payment Result
# --------------------------------------------------------------------------
class PaymentResultView(LoginRequiredMixin, TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get("order_id")
        context["order"] = get_object_or_404(Order, id=order_id, user=self.request.user)
        return context


# --------------------------------------------------------------------------
# Step 7: Order Detail
# --------------------------------------------------------------------------
class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# --------------------------------------------------------------------------
# Step 8: Order List
# --------------------------------------------------------------------------
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")
