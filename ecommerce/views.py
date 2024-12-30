from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action

from .models import BusinessUser, Offer, Category, Product, Order, OrderProduct
from .serializers import (
    BusinessUserSerializer, OfferSerializer, CategorySerializer,
    ProductSerializer, OrderSerializer,PhoneNumberSerializer
)

class BusinessUserDetailView(APIView):
    """
    Retrieve, update, or delete a BusinessUser by their phone number.
    """
    
    def get(self, request, phone):
        # Retrieve BusinessUser by phone
        business_user = BusinessUser.get_user_by_phone(phone)
        if business_user:
            serializer = BusinessUserSerializer(business_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "BusinessUser not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, phone):
        # Delete BusinessUser by phone number
        try:
            business_user = BusinessUser.get_user_by_phone(phone)
            if business_user:
                business_user.delete()
                return Response({"message": "BusinessUser deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            return Response({"detail": "BusinessUser not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        

    
class BusinessUserViewSet(viewsets.ModelViewSet):
    queryset = BusinessUser.objects.all()
    serializer_class = BusinessUserSerializer


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        business_user_phone = request.data.get('business_user_phone')
        product_ids_and_quantities = request.data.get('product_ids_and_quantities')
        billing_address = request.data.get('billing_address')
        order_type = request.data.get('order_type')

        try:
            business_user = BusinessUser.objects.get(phone=business_user_phone)
        except BusinessUser.DoesNotExist:
            return Response({"error": "BusinessUser with this phone number does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price and check for product availability
        total_price = 0
        for product_id, quantity in product_ids_and_quantities.items():
            try:
                product = Product.objects.get(id=product_id)
                if product.stock_quantity < quantity:
                    return Response({"error": f"Not enough stock for product: {product.product_name}"}, status=status.HTTP_400_BAD_REQUEST)
                total_price += product.price * quantity
            except Product.DoesNotExist:
                return Response({"error": f"Product with ID {product_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order
        order_data = {
            'business_user': business_user.id,
            'total_price': total_price,
            'billing_address': billing_address,
            'order_type': order_type
        }

        serializer = OrderSerializer(data=order_data)
        if serializer.is_valid():
            order = serializer.save()

            # Add OrderProducts
            for product_id, quantity in product_ids_and_quantities.items():
                product = Product.objects.get(id=product_id)
                order_product = OrderProduct.objects.create(order=order, product=product, quantity=quantity, price=product.price * quantity)

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class GetUserByPhoneView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get('phone')
            user = BusinessUser.get_user_by_phone(phone)
            if user:
                # Respond with user details
                user_data = {
                    "company_name": user.company_name,
                    "contact_person": user.contact_person,
                    "phone": user.phone,
                    "referral_code": user.referral_code,
                    "cashback_amount": user.cashback_amount,
                }
                return Response(user_data, status=status.HTTP_200_OK)
            else:
                # User not found
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FetchOrdersByCustomerNameView(APIView):
    def get(self, request, company_name):
        orders = Order.get_orders_by_company_name(company_name)
        if not orders.exists():
            return Response({"detail": "No orders found for this company name."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
