from typing import Optional, Any

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.utils.timezone import now

from html_helpers.tables import create_table


def str_or_blank(value: Any) -> str:
    if value is None:
        return ""
    else:
        return str(value)


class Location(models.Model):
    def __str__(self):
        return f"{self.name} {'(archived)' if self.archived else ''}"

    name = models.CharField(max_length=128)
    archived = models.BooleanField(default=False)


class ItemType(models.Model):
    name = models.CharField(max_length=128)
    locations = models.ManyToManyField(Location)

    # sale_price = models.IntegerField(help_text="in ører")

    def __str__(self):
        return self.name


class Session(models.Model):
    start_time = models.DateTimeField(default=now)
    note = models.TextField(blank=True, null=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)

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
        values = {}

        for item in self.itemrecord_set.all():

            try:
                prev_item = previous.itemrecord_set.filter(location=item.location, item_type=item.item_type).first()
                prev_used.append(prev_item.pk)
                prev_amount = prev_item.amount
            except AttributeError:
                prev_amount = 0
            values[(item.item_type, item.location)] = item.amount - prev_amount

        if previous:
            values = {
                **values,
                **{(item.item_type, item.location): -item.amount
                   for item in previous.itemrecord_set.exclude(pk__in=prev_used)}
            }
        return values

    def changes_as_table(self):
        locations = Location.objects.all()
        item_types = ItemType.objects.all()
        values = self.changes()

        def amount_or_none(item_type: ItemType, location: Location) -> Optional[float]:
            try:
                return values[(item_type, location)]
            except KeyError:
                return None

        return create_table(
            ["name"] + [location.name for location in locations] + ["sum"],
            [
                (
                        [item_type.name] +
                        [str_or_blank(amount_or_none(item_type, location)) for location in locations] +
                        [str(sum(amount_or_none(item_type, location) or 0 for location in locations))]
                ) for item_type in item_types
            ]
        )

    @property
    def locations_as_table(self):
        locations = Location.objects.all()
        item_types = ItemType.objects.all()

        def amount_or_none(item_type: ItemType, location: Location) -> Optional[float]:
            record = self.itemrecord_set.filter(item_type=item_type, location=location).first()
            return record.amount if record else None

        return create_table(
            ["name"] + [location.name for location in locations] + ["sum"],
            [
                (
                        [item_type.name] +
                        [str_or_blank(amount_or_none(item_type, location)) for location in locations] +
                        [str(sum(amount_or_none(item_type, location) or 0 for location in locations))]
                ) for item_type in
                item_types]
        )

    def __str__(self):
        return f"{self.start_time.strftime('%d-%m-%y %H:%M')} ({(now() - self.start_time).days} days since) by " \
               f"{self.reporter.get_full_name() if self.reporter.first_name else self.reporter.username}"


class ItemRecord(models.Model):
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    amount = models.FloatField()  # ^[0-9*\-\+ \/\(\)]*$
    # influx = models.BooleanField(default=False) #TODO find out what this was meant to be
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (("item_type", "session", "location"),)
