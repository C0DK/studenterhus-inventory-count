from django.contrib import admin

# Register your models here.
from items.models import ItemType, Location


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    exclude = ["pk"]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    exclude = ["pk"]
