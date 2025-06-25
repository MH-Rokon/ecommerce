from rest_framework import generics, filters, status, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.conf import settings
import stripe
import requests
from bs4 import BeautifulSoup
from .models import Category, Product, Order, Review
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, ReviewSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  


class StandardResultsSetPagination(PageNumberPagination):
    # Pagination class to control page size
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryListCreateView(generics.ListCreateAPIView):
    # List and create categories
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListCreateView(generics.ListCreateAPIView):
    # List and create products with filters and pagination
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering')

        if ordering == 'name_asc':
            queryset = queryset.order_by('name')
        elif ordering == 'name_desc':
            queryset = queryset.order_by('-name')
        elif ordering == 'price_asc':
            queryset = queryset.order_by('price')
        elif ordering == 'price_desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('name')
        return queryset


class OrderListView(generics.ListAPIView):
    # List orders for the logged-in user
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Show only orders of the logged-in user
        return Order.objects.filter(user=self.request.user).order_by('-id')


class CategoryProductSearchAPIView(APIView):
    # Search products within a category with pagination
    pagination_class = StandardResultsSetPagination

    def get(self, request, category_name):
        category_name = category_name.replace('-', ' ')
        category = get_object_or_404(Category, name__iexact=category_name)

        queryset = Product.objects.filter(category=category)

        search_query = request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        ordering = request.query_params.get('ordering')
        if ordering == 'name_asc':
            queryset = queryset.order_by('name')
        elif ordering == 'name_desc':
            queryset = queryset.order_by('-name')
        elif ordering == 'price_asc':
            queryset = queryset.order_by('price')
        elif ordering == 'price_desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('name')

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response({
            'category': category.name,
            'results': serializer.data,
            'count': queryset.count()
        })


class CreateOrderAPIView(APIView):
    # Create an order after validating items and stock
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        items = data.get('items', [])
        total_price = data.get('total_price')

        if not items:
            return Response({'error': 'Order must have items.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate products and stock
        product_ids = [item.get('product_id') for item in items]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {p.id: p for p in products}

        for item in items:
            pid = item.get('product_id')
            qty = item.get('quantity', 0)
            if pid not in product_map:
                return Response({'error': f'Product id {pid} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
            if qty <= 0:
                return Response({'error': 'Quantity must be positive integer.'}, status=status.HTTP_400_BAD_REQUEST)
            product = product_map[pid]
            if product.quantity < qty:
                return Response({'error': f'Insufficient stock for product {product.name}.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create order atomically
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,  # must be logged in because of permission_classes
                items=items,
                total_price=total_price,
                paid=False
            )
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


def reduce_stock_after_payment(order_id):
    # Reduce product stock and mark order paid after payment confirmation
    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order_id)
        if order.paid:
            return  

        for item in order.items:
            product = Product.objects.select_for_update().get(id=item['product_id'])
            if product.quantity < item['quantity']:
                raise Exception(f"Not enough stock for product {product.name}")
            product.quantity -= item['quantity']
            product.save()

        order.paid = True
        order.save()


class StripeWebhookView(APIView):
    # Handle Stripe webhook events
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            # Invalid payload
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            try:
                order = Order.objects.get(stripe_checkout_session_id=session['id'])
                order.paid = True
                order.save()

                reduce_stock_after_payment(order.id)

            except Order.DoesNotExist:
                pass  # Could log this

        return Response(status=status.HTTP_200_OK)


class BookTitlesScraperAPIView(APIView):
    # Scrape book titles from external website
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        url = "https://books.toscrape.com/"
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            books = soup.select("article.product_pod h3 a")
            titles = [book['title'] for book in books]

            return Response({"titles": titles}, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": "Failed to fetch books", "details": str(e)},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    # List and create product reviews filtered by product
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.request.query_params.get('product')
        if product_id:
            return Review.objects.filter(product_id=product_id).order_by('-created_at')
        return Review.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
