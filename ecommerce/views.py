from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.http import JsonResponse

def home_view(request):
    base_url = "https://ecommerce-y7dt.onrender.com"

    data = {
        "message": "Welcome to the E-commerce API",
        "version": "1.0",
        "available_endpoints": {
            "Authentication": {
                "Register": f"{base_url}/api/register/",
                "Activate Account": f"{base_url}/api/activate/<uidb64>/<token>/",
                "Login": f"{base_url}/api/login/",
                "Logout": f"{base_url}/api/logout/",
                "Password Reset Request": f"{base_url}/api/password-reset/",
                "Password Reset Confirm": f"{base_url}/api/reset-password-confirm/<uidb64>/<token>/",
                "User Profile": f"{base_url}/api/profile/"
            },
            "Shop": {
                "Categories": f"{base_url}/myshop/categories/",
                "Products": f"{base_url}/myshop/products/",
                "Orders": f"{base_url}/myshop/orders/",
                "Cart": f"{base_url}/myshop/cart/",
                "Checkout Session": f"{base_url}/myshop/create-checkout-session/",
                "Product Search by Category": f"{base_url}/myshop/category/<category_name>/products/",
                "Stripe Webhook": f"{base_url}/myshop/stripe/webhook/",
                "Books Scraper": f"{base_url}/myshop/books/scrape/",
                "Product Reviews": f"{base_url}/myshop/reviews/"
            },
            "JWT Authentication": {
                "Get Token": f"{base_url}/api/token/",
                "Refresh Token": f"{base_url}/api/token/refresh/"
            }
        },
      
    }

    return JsonResponse(data)
