from django.urls import path
from .views import (
    CategoryListCreateView,
    ProductListCreateView,
    OrderListView,
    CategoryProductSearchAPIView,
    StripeWebhookView,BookTitlesScraperAPIView,ReviewListCreateAPIView
)
from .cart import CartView, CreateCheckoutSessionView

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('cart/', CartView.as_view(), name='cart'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('category/<str:category_name>/products/', CategoryProductSearchAPIView.as_view(), name='category-product-search'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('books/scrape/', BookTitlesScraperAPIView.as_view(), name='books-scrape'),
    path('reviews/', ReviewListCreateAPIView.as_view(), name='review-list'),

]
