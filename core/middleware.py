from .models import Cart


class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.cart = self.get_cart(request)

        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, "context_data"):
            if response.context_data is None:
                response.context_data = {}
            if "cart" not in response.context_data:
                response.context_data["cart"] = request.cart
            else:
                response.context_data["request_cart"] = request.cart
        return response

    # Helper methods

    def get_cart(self, request):
        """
        Return the open Cart for this request
        """
        cart_pk = request.session.get("cart_pk", None)
        if cart_pk:
            session_cart = Cart.objects.filter(pk=cart_pk, status=Cart.OPEN).first()
            if session_cart:
                return session_cart
        cart = Cart.objects.create()
        request.session["cart_pk"] = cart.pk
        return cart
