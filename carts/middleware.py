from .models import Cart


class CartMiddleware:
    """
    Ensures every request has a 'cart' attribute.
    Manage cart functionality for both anonymous and authenticated user.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
            request.cart = cart
        else:
            # associate the cart with the request user
            try:
                request.cart = request.user.cart
            except Cart.DoesNotExist:
                request.cart = Cart.objects.create(user=request.user)

        response = self.get_response(request)
        return response
