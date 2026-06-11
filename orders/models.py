import uuid
from django.db import models
from accounts.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import secrets
from django.core.exceptions import ValidationError
########################################################################################

def generate_order_code():
    return secrets.randbelow(90000000) + 10000000

# --------------------------------------------------------------------------
# 📦 ORDER MODELS
# --------------------------------------------------------------------------
class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        WAITING = "waiting", "پرداخت نشده"
        PAID = "paid", "پرداخت شده"
        FAILED = "failed", "ناموفق"

    class OrderStatus(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        PROCESSING = "processing", "در حال پردازش"
        SHIPPED = "shipped", "ارسال شده"
        COMPLETED = "completed", "تکمیل شده"
        CANCELED = "canceled", "لغو شده"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="orders", blank=True)
    factor_code = models.PositiveIntegerField(default=generate_order_code, unique=True, db_index=True)

    # Customer Snapshot
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    province = models.CharField(max_length=100, blank=False)
    city = models.CharField(max_length=100, blank=False)
    address = models.TextField(blank=False,)
    postal_code = models.CharField(max_length=10, blank=False)
    phone = models.CharField(max_length=11, blank=False)
    note = models.TextField(blank=True)

    # Financial
    discount_amount = models.PositiveBigIntegerField(default=0)
    tax_percent =  models.FloatField(default=0.10)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.WAITING)
    order_status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)

    authority = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    payment_ref_id = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        user_phone = getattr(self.user, "phone", "Guest")
        return f"Order #{self.factor_code} - {getattr(self.user, 'phone', 'Guest')}"

    # -----------------------------
    # Computed Amounts
    # -----------------------------

    @property
    def items_total(self):
        return sum(item.unit_price * item.quantity for item in self.items.all())

    @property
    def total_price(self):
        total = self.items_total - self.discount_amount
        return max(total, 0)

    @property
    def tax_amount(self):
        return int(round(self.total_price * self.tax_percent))

    @property
    def final_price(self):
        return int(self.total_price + self.tax_amount)

########################################################################################
class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    # Generic Product Reference
    product_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    product = GenericForeignKey("product_type", "product_id")

    # Snapshot Fields (VERY IMPORTANT)
    product_name = models.CharField(max_length=255, blank=True)
    unit_price = models.PositiveBigIntegerField()
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("order", "product_type", "product_id")

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"

    @property
    def total_price(self):
        return (self.unit_price or 0) * (self.quantity or 0)

    def save(self, *args, **kwargs):
        if not self.product_name and self.product:
            self.product_name = self.product.name

        if not self.unit_price and self.product:
            self.unit_price = self.product.offer_price or 0

        super().save(*args, **kwargs)
########################################################################################
