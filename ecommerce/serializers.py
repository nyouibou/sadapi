from rest_framework import serializers
from django.db import transaction
from .models import BusinessUser, Offer, Category, Product, Order, OrderProduct


class BusinessUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUser
        fields = [
            'id',
            'company_name',
            'contact_person',
            'phone',
            'uploaded_file',
            'referral_code',
            'cashback_amount',
        ]


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = '__all__'


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'business_user', 'order_date', 'total_price', 'billing_address', 'status', 'order_type', 'cashback_applied', 'order_products']

    def create(self, validated_data):
        order_products_data = validated_data.pop('order_products')
        business_user = validated_data['business_user']
        total_price = sum(item['price'] for item in order_products_data)

        order = Order.objects.create(business_user=business_user, total_price=total_price, **validated_data)

        for order_product_data in order_products_data:
            product = order_product_data['product']
            OrderProduct.objects.create(order=order, product=product, **order_product_data)

        return order

class PhoneNumberSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        """
        Validate phone number format to ensure it adheres to international format.
        """
        import re
        phone_regex = re.compile(r'^\+?1?\d{9,15}$')
        if not phone_regex.match(value):
            raise serializers.ValidationError("Phone number must be in the format: '+999999999'. Up to 15 digits allowed.")
        return value
