from django.conf import settings
from django.db import models
from django.utils import timezone


class VisitorHit(models.Model):
    path = models.CharField(max_length=500, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    user_agent = models.TextField(blank=True, default="")
    referer = models.CharField(max_length=800, blank=True, default="")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="visitor_hits",
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["ip_address", "created_at"]),
        ]

    def __str__(self):
        return f"{self.ip_address} {self.path} {self.created_at:%Y-%m-%d %H:%M}"
