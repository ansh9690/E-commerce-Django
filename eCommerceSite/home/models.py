from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django_extensions.db.fields import AutoSlugField

CATEGORY_CHOICES = (
    ('E', 'earwear'),
    ('L', 'laptop'),
    ('C', 'clothes')
)

LABEL_CHOICES = (
    ('R', 'red'),
    ('G', 'green')
)

ADDRESS_CHOICES = (
    ('B', 'billing'),
    ('S', 'shipping')
)


class Item(models.Model):
    title = models.CharField(max_length=500)
    image = models.ImageField(upload_to="home/products/images")
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    description = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = AutoSlugField(('slug'), max_length=50,
                         unique=True, populate_from=('title',))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("home:product_detail", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("home:add_to_cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("home:remove_from_cart", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)

    coupon = models.ForeignKey(
        'CouponCode', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    recieved = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    '''
    1.Item added to cart
    2.Adding a billing address
        (Failed checkout)
    3.Payment
        (Preprocessing, processing, packaging, etc.)
    4.Being delivered
    5.Recieved
    6.Refund
    '''

    def __str__(self):
        return f"ordered by {self.user.username}"

    def get_total_amount(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.coupon_amount
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    mobile = models.CharField(max_length=10)
    pin_code = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    # country = CountryField(multiple=False)
    state = models.CharField(max_length=2)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)

    amount = models.FloatField()
    timeStamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class CouponCode(models.Model):
    code = models.CharField(max_length=20)
    coupon_amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"
