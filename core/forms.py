from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from core.models import Cart, Order, OrderItem, User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
        )


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)


class OrderCreateForm(forms.ModelForm):
    def __init__(self, user, cart, **kwargs):
        self.user = user
        self.cart = cart
        super(OrderCreateForm, self).__init__(**kwargs)

    class Meta:
        model = Order
        fields = [
            "address",
        ]

    def save(self, commit=True):
        order = super(OrderCreateForm, self).save(commit=False)
        order.user = self.user
        order.first_name = self.user.first_name
        order.last_name = self.user.last_name
        order.email = self.user.email
        order.cart = self.cart
        order.total = self.cart.total

        if commit:
            order.save()
            self.cart.status = Cart.SUBMITTED
            self.cart.save()

            for item in self.cart.items.all():
                OrderItem.objects.create(order=order, price=item.price, car=item.car)

        return order
