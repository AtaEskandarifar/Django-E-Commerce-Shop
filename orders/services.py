from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem
from carts.models import Cart

def create_order_from_cart(user, form):
    """
    Converts a user's cart into an Order with OrderItems.
    Locks the cart and returns the created Order.
    """
    cart = getattr(user, "cart", None)
    if not cart or not cart.items.exists():
        raise ValueError("Cart is empty or missing.")

    with transaction.atomic():
        # -------------------------
        # 1️⃣ Create Order Snapshot
        # -------------------------
        order = Order.objects.create(
            user=user,
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            province=form.cleaned_data["province"],
            city=form.cleaned_data["city"],
            address=form.cleaned_data["address"],
            phone=form.cleaned_data["phone"],
            postal_code=form.cleaned_data["postal_code"],
            note=form.cleaned_data.get("note", ""),
            shipping_method=form.cleaned_data["shipping_method"],
            discount_amount=0,  # could add coupons later
        )

        # -------------------------
        # 2️⃣ Create OrderItems from Cart
        # -------------------------
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_type=item.product_type,
                product_id=item.product_id,
                quantity=item.quantity,
                product_name=item.product.name,
                unit_price=item.product.offer_price
            )

        return order