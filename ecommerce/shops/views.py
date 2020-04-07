from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.
# from django.contrib.staticfiles
from .forms import CheckoutForm
from .models import Item, OrderItem, Order, BillingAddress, Payment
import stripe

stripe.api_key = "pk_test_B471oTONAVuayztFhrOFhxqD00vmj5u5c9"


def products(request):
	context = {

		'items': Item.objects.all()

	}
	return render(request, "products.html", context)

class CheckoutView(View):
	def get(self, *args, **kwargs):
		form = CheckoutForm()
		context = {
			'form': form
		}
		return render(self.request, "checkout.html", context)

	def post(self, *args, **kwargs):
		form = CheckoutForm(self.request.POST or None)
		# Check if user have an order
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			if form.is_valid():
				street_address = form.cleaned_data.get('street_address')
				apartment_address = form.cleaned_data.get('apartment_address')
				country = form.cleaned_data.get('country')
				zip = form.cleaned_data.get('zip')
				# TODO: Functionality for these field
				# same_shippin_address = form.cleaned_data.get(
				# 	'same_shippin_address')
				# save_info = form.cleaned_data.get('save_info')
				payment_option = form.cleaned_data.get('payment_option')

				billing_address = BillingAddress(
					user=self.request.user,
					street_address=street_address,
					apartment_address=apartment_address,
					country=country,
					zip=zip
				)
				billing_address.save()
				order.billing_address = billing_address
				order.save()
				# TODO: add redirect to the selected payment option

				if payment_option == 'S':
					return redirect('shops:payment', payment_option='stripe')
				elif payment_option == 'M':
					return redirect('shops:payment', payment_option='mpesa')
				else:
					messages.warning(self.request, "Invalid payment selected")
					return redirect('shops:checkout')
		except ObjectDoesNotExist:
			messages.error(self.request, "You do not have an active order")
			return redirect("shops:order-summary")

class PaymentView(View):
	def get(self, *args, **kwargs):
		return render(self.request, "payment.html")

def about(request):
	return render(request, "about.html")

class HomeView(ListView):
	model = Item
	paginate_by = 8
	template_name = "home.html"

class PaymentViews(View):
	def get(self, *args, **kwargs):
		order = Order.objects.get(user=self.request.user, ordered=False)
		context = {
			'order': order
		}
		return render(self.request, "payment.html", context)

	def post(self, *args, **kwargs):
		order = Order.objects.get(user=self.request.user, ordered=False)
		token = self.request.POST.get('stripeToken')
		amount = int(order.get_total() * 100)
		try:
			charge = stripe.Charge.create(
			  amount=amount, #cents
			  currency="usd",
			  source=token, # obtained with Stripe.js
			  idempotency_key='PtJwqzZri2xry7MQ',
			)
			# Create the payement
			payement = Payment()
			payment.stipe_change_id = charge['id']
			payment.user = self.request.user
			payment.amount = order.get_total()
			payment.save()

			# assign the payment to the Order
			order.ordered = True
			order.payment = payment
			order.save()

			messages.success(self.request, "Your order was successfull")
			return redirect("/")

		except stripe.error.CardError as e:
			body = e.json_body
			err = body.get('error', {})
			# messages.error(self.request, f"{err.get('message')}")
			message.error(self.request, "%s" %(err.get('message')))
			return redirect("/")

		except stripe.error.RateLimitError as e:
		  # Too many requests made to the API too quickly
		  messages.error(self.request, "Rate limit error")
		  return redirect("/")

		except stripe.error.InvalidRequestError as e:
		  # Invalid parameters were supplied to Stripe's API
		  messages.error(self.request, "Invalid parameters")
		  return redirect("/")

		except stripe.error.AuthenticationError as e:
		  # Authentication with Stripe's API failed
		  # (maybe you changed API keys recently)
		  messages.error(self.request, "Not authenticated")
		  return redirect("/")

		except stripe.error.APIConnectionError as e:
		  # Network communication with Stripe failed
		  messages.error(self.request, "Network Error")
		  return redirect("/")
		except stripe.error.StripeError as e:
		  # Display a very generic error to the user, and maybe send
		  # yourself an email
		  messages.error(self.request, "Something went wrong. you were not charged. Please try again")
		  return redirect("/")
		except Exception as e:
		  # Something else happened, completely unrelated to Stripe
		  # Send an email to ourselves
		  messages.error(self.request, "A serious error occurred. We have been notified")
		  return redirect("/")


# Summary Orders
@method_decorator(login_required, name='dispatch')
# @login_required
class OrderSummaryView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			context = {
				'object': order
			}
			return render(self.request, 'order_summary.html', context)
		except ObjectDoesNotExist:
			messages.error(self.request, "You do not have an active order")
			return redirect("/")

class ItemDetailView(DetailView):
	model = Item
	template_name = "product.html"


@login_required
def add_to_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
		item=item,
		user=request.user,
		ordered=False
	)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]

		# check if the order item is in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item.quantity += 1 
			order_item.save()
			messages.info(request, "This item quantity was updated")
			return redirect("shops:order-summary")
		else:
			order.items.add(order_item)
			messages.info(request, "This item was added to your cart.")
			return redirect("shops:order-summary")			
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(
			user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request, "This item was added to your cart")
	return redirect("shops:order-summary")


@login_required
def remove_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	# Check if user has orders
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]

		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			order.items.remove(order_item)
			messages.info(request, "This Item was removed from cart")
			return redirect("shops:order-summary")
		else:
			messages.info(request, "This was not in Cart")
			return redirect("shops:product", slug=slug)			
	else:
		messages.info(request, "You do not have an active order")
		return redirect("shops:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
	# Check if the order exists
	item = get_object_or_404(Item, slug=slug)
	# Check if user has orders
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]

		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1 
				order_item.save()
			else:
				order.items.remove(order_item)
			messages.info(request, "This Item quantity was updated")
			return redirect("shops:order-summary")
		else:
			messages.info(request, "This was not in Cart")
			return redirect("shops:product", slug=slug)			
	else:
		messages.info(request, "You do not have an active order")
		return redirect("shops:product", slug=slug)