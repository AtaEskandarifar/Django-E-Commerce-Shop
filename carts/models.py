import secrets
import uuid
from django.db import models
from accounts.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
##############################################################################

def generate_cart_code():
    while True:
        code = secrets.randbelow(90000000) + 10000000
        if not Cart.objects.filter(cart_code=code).exists():
            return code

# --------------------------------------------------------------------------
# 🛒 CART MODELS
# --------------------------------------------------------------------------

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    cart_code = models.PositiveIntegerField(default=generate_cart_code, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"CartID '{self.id}' | Cat Code '{self.cart_code}' | UserPhone '{self.user.phone}'"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.select_related())

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())
##############################################################################
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    product = GenericForeignKey("product_type","product_id")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product_type", "product_id")

    def clean(self):
        if self.quantity < 1:
            raise ValidationError("Quantity must be at least 1.")

        if self.quantity > 20:
            raise ValidationError("Maximum 20 units allowed per product.")

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def total_price(self):
        return self.product.offer_price * self.quantity
##############################################################################
