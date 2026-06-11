from django.contrib.sitemaps import Sitemap
from .models import *
from django.http import JsonResponse


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return BlogPost.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.created_at
