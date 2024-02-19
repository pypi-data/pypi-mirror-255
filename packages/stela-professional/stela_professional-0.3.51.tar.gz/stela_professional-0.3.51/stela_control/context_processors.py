from .cart import Cart, SiteData


def cart(request):
    return {'cart': Cart(request)}

def site_data(request):
    return {'site_data': SiteData(request)}