from django.contrib import admin

# Register your models here.
from items.models import ItemType


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    exclude = ["pk"]
