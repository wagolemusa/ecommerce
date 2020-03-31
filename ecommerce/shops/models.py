from django import forms
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
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

class Item(models.Model):
	title = models.CharField(max_length=100)
	price = models.FloatField()
	discount_price = models.FloatField(blank=True, null=True)
	category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
	label = models.CharField(choices=LABEL_CHOICES, max_length=1)
	slug = models.SlugField() 
	description = models.TextField()

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
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username

	# Function get the final tatol 
	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		return total

