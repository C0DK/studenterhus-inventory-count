from django import forms
from django.utils.safestring import mark_safe

from html_helpers.tables import create_table
from items.models import ItemRecord, ItemType, Location, Session


def get_id(item_type: ItemType, location: Location):
    return f"{item_type.name}_{location.name}_amount"


class SessionItemsForm(forms.Form):

    def __init__(self, *args, **kwargs):

        self.instance = kwargs.get('instance', None)
        self.reporter = kwargs.get('reporter', None)

        kwargs = {arg: value for arg, value in kwargs.items() if arg not in ['instance', 'reporter']}
        super().__init__(*args, **kwargs)

        locations = Location.objects.all()
        item_types = ItemType.objects.all()

        for location in locations:
            for item_type in item_types:
                if location in item_type.locations.all():
                    self.fields[get_id(item_type, location)] = forms.IntegerField()

    def as_table(self):
        # THIS IS probably the wrong way of doing this, but i cannot remember how to add widgets from another
        # nested class. and also i want it in the nice table form. so shut up, future me.
        return self.item_types_as_table() + mark_safe("<br>") + str(self.errors)

    def item_types_as_table(self):
        locations = Location.objects.all()
        item_types = ItemType.objects.all()

        def get_default_value(location: Location, item_type: ItemType):
            return self.instance.itemrecord_set.filter(
                location=location,
                item_type=item_type
            ).first().amount if self.instance else ""

        return create_table(
            ["name"] + [location.name for location in locations],
            [
                [item_type.name] +
                [
                    (f'<input name="{get_id(item_type,location)}" step="any" required="" '
                     f'id="{get_id(item_type,location)}" '
                     f'value="{get_default_value(location,item_type)}" '
                     'type="number" class="form-control">') if location in item_type.locations.all() else ""
                    for location in locations
                ] for item_type in item_types
            ]
        )

    def save(self, commit=True):
        if not self.instance:
            self.instance = Session.objects.create(reporter=self.reporter)

        locations = Location.objects.all()
        item_types = ItemType.objects.all()
        for location in locations:
            for item_type in item_types:
                if location in item_type.locations.all():
                    new_amount = self.cleaned_data[get_id(item_type, location)]
                    record, created = ItemRecord.objects.get_or_create(
                        session=self.instance,
                        item_type=item_type,
                        location=location,
                        defaults={
                            'amount': new_amount
                        }
                    )
                    if not created:
                        record.amount = new_amount
                        record.save()
        return self.instance


class SessionNoteForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["note"]
