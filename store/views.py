from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, ProductGallery, ReviewRating
from order.models import OrderProduct
from category.models import Category
from cart.models import CartItem
from .forms import ReviewForm
from cart.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q


# Create your views here.


_NUMBER_OF_PAGE = 12

def store(request, category_slug=None):

    category = None
    products = None

    def get_products(products, num_of_products):
        paginator = Paginator(products, num_of_products)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        return paged_products
    
    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True).order_by('id')
        paged_products = get_products(products, _NUMBER_OF_PAGE)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paged_products = get_products(products, _NUMBER_OF_PAGE)
        product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count,
    }

    return render(request, 'django_ecommerce/store/store.html', context)


def filter_products(request):

    category = None
    products = None

    def get_products(products, num_of_products):
        paginator = Paginator(products, num_of_products)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        return paged_products

    customer_type = ''
    keyword = ''

    if 'keyword' in request.GET or 'customer_type' in request.GET:
        keyword = request.GET.get('keyword', None)
        customer_type = request.GET.get('customer_type', None)

        if keyword and customer_type:
            category = get_object_or_404(Category, slug=keyword)
            if customer_type != 'all':
                products = Product.objects.filter(category=category, customer_type=str(customer_type), is_available=True).order_by('id')
            else:
                products = Product.objects.filter(category=category, is_available=True).order_by('id')
            paged_products = get_products(products, _NUMBER_OF_PAGE)
            product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count,
        'keyword': keyword,
        'customer_type': customer_type,
    }
    return render(request, 'django_ecommerce/store/store.html', context)


def product_detail(request, category_slug, product_slug):

    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        products = Product.objects.filter(category__slug=category_slug, is_available=True).order_by('id').exclude(slug=product_slug)[:20]
        top_products = Product.objects.all().filter(is_available=True).order_by('-price').exclude(slug=product_slug)[:20]
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    context = {
        'single_product': single_product,
        'products': products,
        'top_products': top_products,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }

    return render(request, 'django_ecommerce/store/product_detail.html', context)


def search(request):

    def get_products(products, num_of_products):
        paginator = Paginator(products, num_of_products)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        return paged_products

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            paged_products = get_products(products, _NUMBER_OF_PAGE)
            product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count,
        'keyword': keyword,
    }
    
    return render(request, 'django_ecommerce/store/store.html', context)


def submit_review(request, product_id):
    
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submited.')
                return redirect(url)
