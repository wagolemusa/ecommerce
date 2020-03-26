from django.urls import path

from .views import (
	ItemDetailView,
	checkout,
	HomeView,
	about,
	add_to_cart,
	remove_from_cart,
	
)

app_name = 'shops'
	
urlpatterns = [
	path('', HomeView.as_view(), name='home'),
	path('product/<slug>/', ItemDetailView.as_view(), name='product'),
	path('checkout/', checkout, name='checkout'),
	path('about/', about, name='about'),
	path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
	path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
]