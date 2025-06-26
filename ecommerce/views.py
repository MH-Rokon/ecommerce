from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponse

def home_view(request):
    base_url = "https://ecommerce-y7dt.onrender.com"

    html_content = f"""
    <html>
        <head>
            <title>E-commerce API Home</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 40px;
                    color: #333;
                }}
                h1 {{
                    color: #2980b9;
                }}
                .section {{
                    margin-top: 30px;
                }}
                .endpoint {{
                    margin-left: 20px;
                    color: #2c3e50;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <h1>Welcome to the E-commerce API</h1>
            <p>Click on the text to navigate to the relaed api urls </p>

            <div class="section">
                <h2>Authentication</h2>
                <div class="endpoint"><a href="{base_url}/api/register/">Register</a></div>
                <div class="endpoint"><a href="{base_url}/api/activate/&lt;uidb64&gt;/&lt;token&gt;/">Activate Account</a></div>
                <div class="endpoint"><a href="{base_url}/api/login/">Login</a></div>
                <div class="endpoint"><a href="{base_url}/api/logout/">Logout</a></div>
                <div class="endpoint"><a href="{base_url}/api/password-reset/">Password Reset Request</a></div>
                <div class="endpoint"><a href="{base_url}/api/reset-password-confirm/&lt;uidb64&gt;/&lt;token&gt;/">Password Reset Confirm</a></div>
                <div class="endpoint"><a href="{base_url}/api/profile/">User Profile</a></div>
            </div>

            <div class="section">
                <h2>Shop</h2>
                <div class="endpoint"><a href="{base_url}/myshop/categories/">Categories</a></div>
                <div class="endpoint"><a href="{base_url}/myshop/products/">Products</a></div>
                <div class="endpoint"><a href="{base_url}/myshop/orders/">Orders</a></div>
                <div class="endpoint"><a href="{base_url}/myshop/cart/">Cart</a></div>
                <div class="endpoint"><a href="{base_url}/myshop/create-checkout-session/">Checkout Session</a></div>
                <div class="endpoint"><a href="{base_url}/myshop/category/&lt;category_name&gt;/products/">Product Search by Category</a></div>
                <div class="endpoint"><a href="{base_url}/myshop/stripe/webhook/">Stripe Webhook</a></div>
                <div class="endpoint"><a href="{base_url}/myshop/books/scrape/">Books Scraper</a></div>
                <div class="endpoint"><a href="{base_url}/myshop/reviews/">Product Reviews</a></div>
            </div>

            <div class="section">
                <h2>JWT Authentication</h2>
                <div class="endpoint"><a href="{base_url}/api/token/">Get Token</a></div>
                <div class="endpoint"><a href="{base_url}/api/token/refresh/">Refresh Token</a></div>
            </div>
        </body>
    </html>
    """

    return HttpResponse(html_content)
