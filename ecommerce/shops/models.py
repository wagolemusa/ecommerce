from django import forms
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField
# Create your models here.

CATEGORY_CHOICES = (
	('S',  'Shirts'),
	('SW', 'Sport weare'),
	('OW', 'Outwear')
)

LABEL_CHOICES = (
	('P', 'primary'),
	('S', 'secondary'),
	('D', 'danger')
)

ADDRESS_CHOICES = (
	('B', 'Billing'),
	('S', 'Shipping'),
)

class Item(models.Model):
	title = models.CharField(max_length=100)
	price = models.FloatField()
	discount_price = models.FloatField(blank=True, null=True)
	category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
	label = models.CharField(choices=LABEL_CHOICES, max_length=1)
	slug = models.SlugField() 
	description = models.TextField()
	# image = models.ImageField(blank=True, null=True)
	image = models.ImageField()

	def __str__(self):
		return self.title

	def get_absolete_url(self):
		return reverse("shops:product", kwargs={
				'slug': self.slug
			})

	def get_add_to_cart_url(self):
		return reverse("shops:add-to-cart", kwargs={
			'slug': self.slug
			})

	def get_remove_from_cart_url(self):
		return reverse("shops:remove-from-cart", kwargs={
			'slug':self.slug
			})

class OrderItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
													on_delete=models.CASCADE)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	ordered = models.BooleanField(default=False)

	def __str__(self):
		return "%s %s" %(self.quantity, self.item.title)
	
	# Total quantity price
	def get_total_item_price(self):
		return self.quantity * self.item.price

	# Discount on Items
	def get_discount_item_price(self):
		return self.quantity * self.item.discount_price

	def get_amount_saved(self):
		return self.get_total_item_price() - self.get_discount_item_price()

	# Function return the final total price
	def get_final_price(self):
		if self.item.discount_price:
			return self.get_discount_item_price()
		return self.get_total_item_price()


class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
													on_delete=models.CASCADE)
	ref_code = models.CharField(max_length=20, blank=True, null=True)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	shipping_address = models.ForeignKey(
		'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
	billing_address = models.ForeignKey(
		'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
	payment = models.ForeignKey(
		'Payment', on_delete=models.SET_NULL, blank=True, null=True)
	mpesa_pay = models.ForeignKey(
		'Mpesapay', on_delete=models.SET_NULL, blank=True, null=True)
	coupon = models.ForeignKey(
		'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
	being_delivered = models.BooleanField(default=False)
	received_requested = models.BooleanField(default=False)
	refund_requested = models.BooleanField(default=False)
	refund_granted = models.BooleanField(default=False)

	'''
	1. Item added to cart
	2. Adding a billing address
	(Failed checkout)
	3. payment
		(Preprocessing, processing, packing, etc)
	4. Being delivered
	5. Received
	6. Refunds
	'''

	def __str__(self):
		return self.user.username

	# Function get the final tatol 
	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		if self.coupon:
			total -= self.coupon.amount
		return total

class Address(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
														on_delete=models.CASCADE)
	street_address = models.CharField(max_length=100)
	apartment_address = models.CharField(max_length=100)
	country = CountryField(multiple=False)
	zip = models.CharField(max_length=100)
	address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
	default = models.BooleanField(default=False)
	def __str__(self):
		return self.user.username

	class Meta:
		verbose_name_plural = 'address'

class Payment(models.Model):
	stripe_change_id = models.CharField(max_length=50)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
													on_delete=models.SET_NULL, blank=True, null=True)
	amount = models.FloatField()
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__self(self):
		return self.user.username

		
class Mpesapay(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
													on_delete=models.SET_NULL, blank=True, null=True)
	amount = models.FloatField()
	phone = models.IntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__self(self):
		return self.user.username


class Coupon(models.Model):
	code = models.CharField(max_length=15)
	amount = models.FloatField()

	def __str__(self):
		return self.code 

class Refund(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	reason = models.TextField()
	accepted = models.BooleanField(default=False)
	email = models.EmailField()

	def __str__(self):
		return "%s" %(self.pk)
