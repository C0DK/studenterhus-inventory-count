from typing import Optional, Tuple

from django.db import models
from django.db.models import Sum
from django.utils.timezone import now


class ItemChange:
    def __init__(self, in_bar: bool, type: "ItemType", amount: float):
        self.amount = amount
        self.type = type
        self.in_bar = in_bar

    def __str__(self):
        return f"{self.type} {'bar' if self.in_bar else 'storage'} {self.amount}"


class ItemType(models.Model):
    name = models.CharField(max_length=128)
    locations = models.CharField(max_length=4)
    sale_price = models.IntegerField(help_text="in ører")

    def __str__(self):
        return self.name


class Session(models.Model):
    start_time = models.DateTimeField(default=now)
    note = models.TextField(blank=True, null=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def amount_of_type(self, item_type: ItemType):
        return sum(i.amount for i in self.itemrecord_set.filter(type=item_type))

    @property
    def previous(self) -> Optional["Session"]:
        return Session.objects.filter(pk__lt=self.pk).last()

    @property
    def next(self) -> Optional["Session"]:
        return Session.objects.filter(pk__gt=self.pk).first()

    def total(self):
        return self.itemrecord_set.values('type').annotate(count=Sum('amount'))

    def changes(self):
        previous = self.previous
        prev_used = []
        values = []

        for item in self.itemrecord_set.all():
            prev_item = previous.itemrecord_set.filter(location=item.location, type=item.type).first()
            prev_used.append(prev_item.pk)
            values.append(ItemChange(item.in_bar, item.type, prev_item.amount - item.amount))

        values += [ItemChange(item.in_bar, item.type, -item.amount)
                   for item in previous.itemrecord_set.exclude(pk__in=prev_used)]

        return values


LOCATIONS = [
    (0, "bar"),
    (1, "storage"),
    (2, "concert_hall"),
    (3, "star_gate"),

]


class ItemRecord(models.Model):
    type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    location = models.IntegerField(choices=LOCATIONS)
    amount = models.FloatField()  # ^[0-9*\-\+ \/\(\)]*$
    influx = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (("type", "session", "location", "influx"),)
