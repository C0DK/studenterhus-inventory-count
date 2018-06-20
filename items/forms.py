from django import forms

from items.models import ItemRecord


class ItemRecordForm(forms.ModelForm):
    class Meta:
        model = ItemRecord
        exclude = ["pk","type","session","location"]
