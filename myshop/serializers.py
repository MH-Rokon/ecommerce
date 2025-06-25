from rest_framework import serializers
from .models import Category, Product, Order
from .models import Review



class CategorySerializer(serializers.ModelSerializer):
    # Serializer for Category model
    class Meta:
        model = Category
        fields = ['id', 'name']
        
        
        

class ProductSerializer(serializers.ModelSerializer):
    # Serializer for Product model with nested Category and writable category_id
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'category_id', 'created_at']



class OrderSerializer(serializers.ModelSerializer):
    # Serializer for Order model with validation on items
    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'created_at', 'paid', 'stripe_payment_intent']
        read_only_fields = ['id', 'created_at', 'paid', 'stripe_payment_intent']

    def validate_items(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Items must be a list.")
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each item must be a dictionary.")
            if 'product_id' not in item:
                raise serializers.ValidationError("Each item must have a 'product_id'.")
            if 'quantity' not in item:
                raise serializers.ValidationError("Each item must have a 'quantity'.")
            quantity = item['quantity']
            if not isinstance(quantity, int) or quantity <= 0:
                raise serializers.ValidationError("Quantity must be a positive integer.")
        return value





class ReviewSerializer(serializers.ModelSerializer):
    # Serializer for Review model with read-only user field
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
