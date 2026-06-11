from django.contrib.sitemaps import Sitemap
from .models import *
from django.http import JsonResponse

class ProductSitemap(Sitemap):
    changefreq = "daily"
    protocol = "https"
    priority = 0.8

    # این متد باید ترکیبی از همه محصولات باشد
    def items(self):
        # می‌توانید فیلتر کنید که فقط محصولات فعال نمایش داده شوند
        return list(CLP.objects.filter(is_active=True)) + \
               list(AMP.objects.filter(is_active=True)) + \
               list(Equipment.objects.filter(is_active=True)) + \
               list(GuitarStrings.objects.filter(is_active=True))

    def lastmod(self, obj):
        return obj.created_at
