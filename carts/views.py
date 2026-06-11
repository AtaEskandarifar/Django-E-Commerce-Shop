from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import *
from .models import *
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.db import transaction
from django.db.models import F
######################################################################################
class CartView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request):
        product_id = request.POST.get("product_id")
        product_model = request.POST.get("product_model")

        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            quantity = 1

        MAX_PER_ITEM = 20
        if quantity > MAX_PER_ITEM:
            quantity = MAX_PER_ITEM

        model_map = {
            "clp": CLP,
            "amp": AMP,
            "equipment": Equipment,
            "guitarstrings": GuitarStrings,
        }

        if not product_model:
            return JsonResponse({"success": False, "error": "محصول معتبر نیست."}, status=400)

        model = model_map.get(product_model.lower())
        if not model:
            return JsonResponse({"success": False, "error": "محصول یافت نشد."}, status=404)

        try:
            product = model.objects.get(pk=product_id)
        except model.DoesNotExist:
            return JsonResponse({"success": False, "error": "محصول یافت نشد."}, status=404)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        content_type = ContentType.objects.get_for_model(product)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_type=content_type,
            product_id=product.id,
            defaults={"quantity": quantity},
        )

        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > MAX_PER_ITEM:
                new_quantity = MAX_PER_ITEM
            cart_item.quantity = new_quantity
            cart_item.save()

        request.session.modified = True

        return JsonResponse({
            "success": True,
            "message": "محصول به سبد خرید اضافه شد."
        })
######################################################################################
class CartItemsView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = (
            CartItem.objects
            .filter(cart__user=request.user)
            .select_related("product_type")
        )

        items_data = []
        total = 0

        for item in cart_items:
            product = item.product
            if not product:
                continue

            unit_price = getattr(product, "offer_price", 0) or 0
            quantity = item.quantity
            item_total = unit_price * quantity

            items_data.append({
                "id": item.id,
                "name": product.name,
                "image": product.image.url if getattr(product, "image", None) else "",
                "quantity": quantity,
                "unit_price": unit_price,
                "item_total": item_total,
            })

            total += item_total

        return JsonResponse({
            "items": items_data,
            "total": total,
            "count": cart_items.count(),
        })
######################################################################################
class CartItemDeleteView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user
        )

        cart_item.delete()
        request.session.modified = True

        cart_count = CartItem.objects.filter(
            cart__user=request.user
        ).count()

        return JsonResponse({
            "success": True,
            "cart_count": cart_count
        })

######################################################################################
class CartPageView(LoginRequiredMixin, TemplateView):
    template_name = "mobilecart.html"