from django.contrib import admin

# Register your models here.
from core.models import Brand, Car, User


@admin.register(User)
class CarAdmin(admin.ModelAdmin):
    pass


@admin.register(Brand)
class CarAdmin(admin.ModelAdmin):
    pass


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    pass
