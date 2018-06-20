from django.shortcuts import render

# Create your views here.
from items.forms import ItemRecordForm
from items.models import ItemType, LOCATIONS


def location_from_id(location):
    return LOCATIONS[location][1]


def create_new_session(request):
    forms = [{
        "form": ItemRecordForm(prefix=it.pk),
        "location": location_from_id(idx),
        "type": it
    }
        for it in ItemType.objects.all() for idx, loc in enumerate(it.locations) if loc == "1"]

    return render(request, "form_new_session.html", {
        "forms": forms
    })

def view_history(request):
    pass
