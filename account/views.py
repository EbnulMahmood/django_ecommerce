from cart.models import Cart, CartItem
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from order.models import Order, OrderProduct
from cart.views import _cart_id

from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests
from django.core.paginator import Paginator


# Create your views here.


@require_http_methods(['POST', 'GET'])
def register(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    elif request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, 
                    email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('django_ecommerce/account/account_varification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            return redirect('/account/login/?command=varification&email=' + email)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }

    return render(request, 'django_ecommerce/account/register.html', context)


# @require_http_methods(['POST', 'GET'])
def login(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                if CartItem.objects.filter(cart=cart).exists():
                    cart_items = CartItem.objects.filter(cart=cart)
                    product_variation = []
                    for item in cart_items:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    
                    cart_items = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_items:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for product in product_variation:
                        if product in ex_var_list:
                            index = ex_var_list.index(product)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_items = CartItem.objects.filter(cart=cart)
                            for item in cart_items:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            # messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials.', extra_tags='danger')
            return redirect('login')

    return render(request, 'django_ecommerce/account/login.html')


@login_required(login_url='login')
def logout(request):

    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


@require_http_methods(['POST', 'GET'])
def activate(request, uidb64, token):

    if request.user.is_authenticated:
        return redirect('dashboard')
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link', extra_tags='danger')
        return redirect('register')


_NUMBER_OF_PAGE = 3
@login_required(login_url='login')
def dashboard(request):

    def get_orders(orders, num_of_orders):
        paginator = Paginator(orders, num_of_orders)
        page = request.GET.get('page')
        paged_orders = paginator.get_page(page)
        return paged_orders

    if not request.user.is_authenticated:
        return redirect('login')

    else:
        orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
        paged_orders = get_orders(orders, _NUMBER_OF_PAGE)
        orders_count = orders.count()
        try:
            userprofile = UserProfile.objects.get(user_id=request.user.id)
        except UserProfile.DoesNotExist:
            userprofile = None

    context = {
        'orders': paged_orders,
        'orders_count': orders_count,
        'userprofile': userprofile,
    }

    return render(request, 'django_ecommerce/account/dashboard.html', context)


@require_http_methods(['POST', 'GET'])
def forgot_password(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    elif request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('django_ecommerce/account/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Reset password email has been sent at ' + email)
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist!', extra_tags='danger')
            return redirect('forgot_password')

    return render(request, 'django_ecommerce/account/forgot_password.html')


@require_http_methods(['POST', 'GET'])
def reset_password_validate(request, uidb64, token):

    if request.user.is_authenticated:
        return redirect('dashboard')
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!', extra_tags='danger')
        return redirect('login')


@require_http_methods(['POST', 'GET'])
def reset_password(request):

    if request.user.is_authenticated:
        return redirect('dashboard')
    
    elif request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful!')
            return redirect('login')
        else:
            messages.error(request, 'Password does not match!', extra_tags='danger')
            return redirect('reset_password')
    
    return render(request, 'django_ecommerce/account/reset_password.html')


@login_required(login_url='login')
def my_orders(request):

    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'django_ecommerce/account/my_orders.html', context)



@login_required(login_url='login')
def edit_profile(request):

    try:
        userprofile = get_object_or_404(UserProfile, user=request.user)
        if request.method == 'POST':
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('edit_profile')
        else:
            user_form = UserForm(instance=request.user)
            profile_form = UserProfileForm(instance=userprofile)
    except:
        userprofile = UserProfile(user=request.user)
        userprofile.save()
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'django_ecommerce/account/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):

    if not request.user.is_authenticated:
        return redirect('login')
    elif request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request, 'Password updated successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Invalid current password!', extra_tags='danger')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!', extra_tags='danger')
            return redirect('change_password')

    return render(request, 'django_ecommerce/account/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):

    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)

    subtotal = 0
    for item in order_detail:
        subtotal += item.product_price * item.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'django_ecommerce/account/order_detail.html', context)
