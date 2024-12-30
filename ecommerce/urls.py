from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register("business_users", BusinessUserViewSet)
router.register("offers", OfferViewSet)
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
router.register("orders", OrderViewSet)
# router.register("ordersproducts", OrderProductViewSet)



urlpatterns = [
    path("", include(router.urls)),
    path('business_user/<str:phone>/', BusinessUserDetailView.as_view(), name='business_user_detail'),
    path('orders/by_customer/<str:company_name>/', FetchOrdersByCustomerNameView.as_view(), name='orders-by-customer'),
]
