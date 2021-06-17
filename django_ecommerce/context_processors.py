

def page_title(request):
    
    if '/store/category/' in request.path:
        product_name = request.path.replace('/store/category/', '')[:-1]
        page_title = '/'.join(product_name.split('/')[1:]).capitalize()
        return dict(page_title=page_title)
        
    elif '/order/order_complete/' in request.path:
        return dict(page_title='Receipt')

    elif '/order/place_order/' in request.path:
        return dict(page_title='Payment')
    
    elif '/cart/checkout/' in request.path:
        return dict(page_title='Checkout')
    
    elif '/cart/' in request.path:
        return dict(page_title='Cart')

    elif '/account/login/' in request.path:
        return dict(page_title='Login')
    
    elif '/account/register/' in request.path:
        return dict(page_title='Register')

    elif '/account/reset_password/' in request.path:
        return dict(page_title='Reset Password')
    
    elif '/account/forgot_password/' in request.path:
        return dict(page_title='Forgot Password')

    elif '/account/dashboard/' in request.path:
        return dict(page_title='Dashboard')

    elif '/account/my_orders/' in request.path:
        return dict(page_title='My Orders')

    elif '/account/edit_profile/' in request.path:
        return dict(page_title='Edit Profile')

    elif '/account/change_password/' in request.path:
        return dict(page_title='Change Password')
    
    elif '/account/order_detail/' in request.path:
        return dict(page_title='Receipt')

    elif '/store/' in request.path:
        return dict(page_title='Store')

    elif '' in request.path:
        return dict(page_title='Fashion & Lifestyle')