from .models import VisitorHit


def visitor_analytics(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        visitor_ip = x_forwarded_for.split(",")[0].strip()
    else:
        visitor_ip = request.META.get("REMOTE_ADDR", "")

    if not request.session.get("visited"):
        VisitorHit.objects.create(
            path=request.path[:500],
            ip_address=visitor_ip or None,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            referer=request.META.get("HTTP_REFERER", "")[:800],
            user=request.user if request.user.is_authenticated else None,
        )
        request.session["visited"] = True

    total_visits = VisitorHit.objects.count()

    return {
        "visitor_ip": visitor_ip,
        "total_visits": total_visits,
    }
