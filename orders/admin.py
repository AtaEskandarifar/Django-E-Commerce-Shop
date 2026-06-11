from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    readonly_fields = (
        "product_name_display",
        "quantity",
        "unit_price_display",
        "total_price_display",
    )

    @admin.display(description="محصول")
    def product_name_display(self, obj):
        return obj.product_name

    @admin.display(description="قیمت واحد")
    def unit_price_display(self, obj):
        if not obj.unit_price:
            return "-"
        return f"{obj.unit_price:,} تومان"

    @admin.display(description="جمع")
    def total_price_display(self, obj):
        if not obj.unit_price:
            return "-"
        try:
            total = obj.unit_price * obj.quantity
        except:
            return "-"
        return f"{total:,} تومان"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "factor_code",
        "user",
        "payment_status_colored",
        "order_status",
        "total_price_display",
        "created_at",
    )

    list_filter = (
        "payment_status",
        "order_status",
        "created_at",
    )

    search_fields = (
        "=factor_code",
        "user__phone",
        "user__email",
        "payment_ref_id",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "id",
        "factor_code",
        "payment_status",
        "payment_ref_id",
        "paid_at",
        "created_at",
        "items_total_display",
        "total_price_display",
        "tax_percent",
        "tax_amount_display",
        "final_price_display",
    )

    inlines = [OrderItemInline]

    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("id", "factor_code", "user", "created_at")
        }),
        ("اطلاعات مشتری", {
            "fields": (
                "first_name",
                "last_name",
                "phone",
                "province",
                "city",
                "address",
                "postal_code",
                "note",
            )
        }),
        ("وضعیت", {
            "fields": (
                "payment_status",
                "order_status",
                "payment_ref_id",
                "paid_at",
            )
        }),
        ("مالی", {
            "fields": (
                "items_total_display",
                "discount_amount",
                "tax_percent",
                "tax_amount_display",
                "total_price_display",
                "final_price_display",
            )
        }),
    )

    @admin.display(description="وضعیت پرداخت")
    def payment_status_colored(self, obj):
        color = {
            "paid": "green",
            "failed": "red",
            "waiting": "orange",
        }.get(obj.payment_status, "black")

        return format_html(
            '<span style="color:{};"><strong>{}</strong></span>',
            color,
            obj.get_payment_status_display(),
        )

    @admin.display(description="جمع محصولات")
    def items_total_display(self, obj):
        return f"{obj.items_total:,} تومان"

    @admin.display(description="جمع کل")
    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"

    @admin.display(description="مالیات")
    def tax_amount_display(self, obj):
        return f"{obj.tax_amount:,} تومان"

    @admin.display(description="مبلغ نهایی پرداختی")
    def final_price_display(self, obj):
        return f"{obj.final_price:,} تومان"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("items")
