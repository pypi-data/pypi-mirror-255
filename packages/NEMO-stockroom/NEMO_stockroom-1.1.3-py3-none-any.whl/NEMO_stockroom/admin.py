from django.contrib import admin
from django.contrib.admin import register

from NEMO_stockroom.models import (
	ConsumableRequest, QuantityModification, ConsumableThumbnail
)


@register(ConsumableRequest)
class ConsumableRequestAdmin(admin.ModelAdmin):
	list_display = ("customer", "consumable", "quantity", "project", "date")

@register(QuantityModification)
class QuantityModificationAdmin(admin.ModelAdmin):
	list_display = ("consumable", "old_qty", "new_qty", "modifier")

@register(ConsumableThumbnail)
class ConsumableThumbnailAdmin(admin.ModelAdmin):
	list_display = ("consumable", "image")