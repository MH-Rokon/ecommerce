from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
import stripe

from .models import Product, Order

stripe.api_key = settings.STRIPE_SECRET_KEY

CART_SESSION_ID = 'cart'


class CartView(APIView):
    # Handles retrieving and modifying the user's cart stored in session
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        cart = request.session.get(CART_SESSION_ID, {})
        products = Product.objects.filter(id__in=cart.keys())
        serialized = []
        for product in products:
            serialized.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'image': request.build_absolute_uri(product.image.url) if product.image else None,
                'quantity': cart.get(str(product.id), 0),
            })
        total_price = sum(item['price'] * item['quantity'] for item in serialized)
        return Response({'cart_items': serialized, 'total_price': total_price})

    def post(self, request):
        try:
            product_id = str(request.data.get('product_id'))
            quantity_raw = request.data.get('quantity', 1)
            quantity = int(quantity_raw)

            if not product_id or quantity < 1:
                return Response({'error': 'Invalid product_id or quantity'}, status=status.HTTP_400_BAD_REQUEST)

            product = Product.objects.get(pk=product_id)

            if product.quantity < quantity:
                return Response({'error': f'Only {product.quantity} items left in stock'}, status=status.HTTP_400_BAD_REQUEST)

            cart = request.session.get(CART_SESSION_ID, {})
            cart[product_id] = quantity
            request.session[CART_SESSION_ID] = cart
            request.session.modified = True

            return Response({'message': f'Added product {product_id} quantity {quantity} to cart.'})

        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response({'error': 'Quantity must be a valid integer.'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        product_id = str(request.data.get('product_id'))
        if not product_id:
            return Response({'error': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)
        cart = request.session.get(CART_SESSION_ID, {})
        if product_id in cart:
            del cart[product_id]
            request.session[CART_SESSION_ID] = cart
            request.session.modified = True
            return Response({'message': 'Product removed from cart.'})
        return Response({'error': 'Product not in cart'}, status=status.HTTP_404_NOT_FOUND)


class CreateCheckoutSessionView(APIView):
    # Creates a Stripe checkout session and stores order info in DB
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = request.session.get(CART_SESSION_ID, {})
        if not cart:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.filter(id__in=cart.keys())

        line_items = []
        order_items = []
        total_price = 0

        for product in products:
            quantity = cart.get(str(product.id), 0)
            if quantity > 0:
                if product.quantity < quantity:
                    return Response(
                        {'error': f'Not enough stock for product {product.name}. Only {product.quantity} left.'},
                        status=status.HTTP_400_BAD_REQUEST)

                amount_cents = int(product.price * 100)
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': product.name},
                        'unit_amount': amount_cents,
                    },
                    'quantity': quantity,
                })
                order_items.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': quantity,
                })
                total_price += product.price * quantity

        if not line_items:
            return Response({'error': 'No valid products in cart'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f'{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{settings.FRONTEND_URL}/cancel',
            )

            Order.objects.create(
                user=request.user,
                items=order_items,
                total_price=total_price,
                paid=False,
                stripe_payment_intent=session.payment_intent if hasattr(session, 'payment_intent') else None,
                stripe_checkout_session_id=session.id,
            )

            return Response({'checkout_session_id': session.id})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
