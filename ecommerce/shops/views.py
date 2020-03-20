from django.shortcuts import render
from django.views.generic import ListView, DetailView
# Create your views here.

from .models import Item

def products(request):
	context = {

		'items': Item.objects.all()

	}
	return render(request, "products.html", context)

def checkout(request):
	return render(request, "checkout.html")

def about(request):
	return render(request, "about.html")

class HomeView(ListView):
	model = Item
	template_name = "home.html"

class ItemDetailView(DetailView):
	model = Item
	template_name = "product.html"

