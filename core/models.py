from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and
        password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = UserManager.normalize_email(email)
        user = self.model(
            email=email,
            is_active=True,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(TimeStampedModel, AbstractUser):
    username = None
    email = models.EmailField(_("email address"), blank=False, null=False, unique=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.get_full_name()


class Brand(TimeStampedModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(null=True)

    def __str__(self):
        return self.name


class CarQuerySet(QuerySet):
    def recent(self):
        return self.order_by("-created")[:20]


class Car(TimeStampedModel):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    description = models.TextField(default="")
    image = models.ImageField(null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)

    objects = CarQuerySet.as_manager()

    def __str__(self):
        return self.name


class Cart(TimeStampedModel):
    # Cart statuses
    OPEN, SUBMITTED = ("Open", "Submitted")
    STATUS_CHOICES = (
        (OPEN, _("Open - currently active")),
        (SUBMITTED, _("Submitted - has been ordered at the checkout")),
    )
    status = models.CharField(
        _("Status"), max_length=128, default=OPEN, choices=STATUS_CHOICES
    )

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def __str__(self):
        return f"{self.id} - {self.get_status_display()}"

    @property
    def total(self):
        return sum([item.price for item in self.items.all()])

    def submit(self):
        self.status = self.SUBMITTED
        self.save()


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(
        Cart,
        verbose_name=_("Cart"),
        related_name="items",
        on_delete=models.CASCADE,
    )
    car = models.ForeignKey(
        Car,
        verbose_name=_("Car"),
        related_name="cart_items",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")

    def __str__(self):
        return f"line for {self.car}"

    @property
    def price(self):
        """
        Calculate the total price for the current screen booking based on
        number of slots and duration.
        """
        return self.car.price


class Order(TimeStampedModel):
    email = models.EmailField(_("Email"), null=True, blank=True)
    address = models.CharField(_("Address"), max_length=100, blank=True, null=True)
    first_name = models.CharField(
        _("first name"), max_length=150, blank=True, null=True
    )
    last_name = models.CharField(_("last name"), max_length=150, blank=True, null=True)

    total = models.DecimalField(_("Total"), max_digits=12, decimal_places=3)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.id} - {self.email}"

    def get_absolute_url(self):
        return reverse("order_detail", args=(self.pk,))


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        Order,
        verbose_name=_("Order"),
        related_name="items",
        on_delete=models.CASCADE,
    )
    car = models.ForeignKey(
        Car,
        related_name="order_cars",
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=3)

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.car}"
