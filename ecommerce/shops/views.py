from django.shortcuts import render

# Create your views here.

from .models import Item

def item_list(request):
	context = {

		'items': Item.objects.all()

	}
	return render(request, "home-page.html", context)
