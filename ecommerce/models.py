from django.db import models


class BusinessUser(models.Model):
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)  # Ensure phone number is unique for easier querying
    uploaded_file = models.FileField(upload_to='business_user_files/', blank=True, null=True)  # Optional field
    referral_code = models.CharField(max_length=50, blank=True, null=True)
    cashback_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.company_name

    def apply_referral_cashback(self, total_order_amount):
        if self.referral_code == "leafcoin":
            cashback = total_order_amount * 0.05
            self.cashback_amount += cashback
            self.save()
            return cashback
        return 0

    @classmethod
    def get_user_by_phone(cls, phone):
        """
        Fetches a BusinessUser instance by phone number.
        Returns the user if found, otherwise returns None.
        """
        try:
            return cls.objects.get(phone=phone)
        except cls.DoesNotExist:
            return None


class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.FloatField()
    applicable_minimum_quantity = models.IntegerField()
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to="categories/images/", blank=True, null=True)  # New image field

    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_details = models.TextField()
    image = models.ImageField(upload_to="products/images/")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_quantity = models.IntegerField()
    stock_quantity = models.IntegerField(default=0)  # New field for available stock
    is_in_stock = models.BooleanField(default=True)  # New field for stock status

    def save(self, *args, **kwargs):
        # Automatically set `is_in_stock` based on `stock_quantity`
        self.is_in_stock = self.stock_quantity > 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    ORDER_TYPE_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
    ]
    business_user = models.ForeignKey(BusinessUser, related_name="orders", on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_address = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    order_type = models.CharField(max_length=50, choices=ORDER_TYPE_CHOICES)
    cashback_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @classmethod
    def get_orders_by_company_name(cls, company_name):
        return cls.objects.filter(business_user__company_name__icontains=company_name)

    def save(self, *args, **kwargs):
        if not self.pk:
            cashback = self.business_user.apply_referral_cashback(self.total_price)
            self.cashback_applied = cashback
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.business_user.company_name}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name="order_products", on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} for Order {self.order.id}"