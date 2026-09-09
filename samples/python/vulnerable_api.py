import json
import pickle
from django.http import JsonResponse
from django.db import connection
from myapp.models import User, Order

API_KEY = "sk_live_hardcoded_key"
DB_PASSWORD = "super-secret-prod-password"


def get_user_orders(request):
    user_id = request.GET.get("user_id")

    # SQL Injection vulnerability
    query = f"SELECT * FROM orders WHERE user_id = {user_id}"
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Unsafe deserialization
    profile = pickle.loads(request.body)

    try:
        enriched = []
        for user in User.objects.all():
            # N+1 query in loop
            user_orders = Order.objects.filter(user=user)
            for order in user_orders:
                enriched.append({"user": user.username, "order": order.id})

        # Performance issue: nested loops
        matches = []
        for row in rows:
            for item in enriched:
                if item["order"] == row[0]:
                    matches.append(item)
    except:
        # Bare except
        pass

    # Missing error handling for invalid JSON payload
    metadata = json.loads(profile.get("metadata", "{}"))
    return JsonResponse({"rows": rows, "matches": matches, "metadata": metadata, "api_key": API_KEY})
