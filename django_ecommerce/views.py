from store.models import Product
from django.shortcuts import render
from store.models import Product, ReviewRating


def home(request):

    products = Product.objects.all().filter(is_available=True).order_by('-created_date')[:8]

    top_products = Product.objects.all().filter(is_available=True).order_by('-price')[:20]

    reviews = None
    if products:
        for product in products:
            reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'top_products': top_products,
        'reviews': reviews,
    }

    return render(request, 'django_ecommerce/home.html', context)