from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.contrib.auth.views import RedirectURLMixin

# Create your views here.
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import LoginForm, OrderCreateForm, RegisterForm
from .models import Brand, Car, CartItem, Order


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super(HomePageView, self).get_context_data(**kwargs)
        ctx["cars"] = Car.objects.recent()
        ctx["brands"] = Brand.objects.all()
        return ctx


class CarListView(ListView):
    queryset = Car.objects.all()
    template_name = "browse.html"
    context_object_name = "cars"

    def get_queryset(self):
        qs = super(CarListView, self).get_queryset()
        search = self.request.GET.get("q", None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            ).distinct()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["brands"] = Brand.objects.all()
        try:
            ctx["selected_brand"] = int(self.request.GET.get("brand", None))
        except:
            pass
        return ctx


class CarDetailView(DetailView):
    queryset = Car.objects.all()
    template_name = "details.html"


class RegisterView(CreateView):
    template_name = "register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("login")


class LoginView(BaseLoginView):
    template_name = "login.html"
    success_url = "/"
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data["remember_me"]
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super(LoginView, self).form_valid(form)


class LogoutView(BaseLogoutView):
    pass


class CartView(TemplateView):
    template_name = "cart.html"


class CartAddView(RedirectURLMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        car = get_object_or_404(Car, pk=request.POST.get("car", None))
        cart = request.cart
        CartItem.objects.create(cart=cart, car=car)
        redirect_url = self.get_redirect_url() or reverse("car_detail", args=(car.pk,))
        return redirect(redirect_url)


class CartRemoveView(RedirectURLMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        CartItem.objects.filter(pk=request.POST.get("item", None)).delete()
        redirect_url = self.get_redirect_url() or reverse("cart")
        return redirect(redirect_url)


class CheckoutView(LoginRequiredMixin, CreateView):
    http_method_names = ["post"]
    form_class = OrderCreateForm

    def get_form_kwargs(self):
        ctx = super(CheckoutView, self).get_form_kwargs()
        ctx["user"] = self.request.user
        ctx["cart"] = self.request.cart
        return ctx


class OrderDetailView(LoginRequiredMixin, DetailView):
    queryset = Order.objects.all()
    template_name = "order.html"
    context_object_name = "order"
