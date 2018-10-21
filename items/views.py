from django.shortcuts import render, redirect, get_object_or_404

from items.forms import SessionItemsForm, SessionNoteForm
from items.models import Session


def create_session(request, session_pk=None):
    form = SessionItemsForm(
        request.POST or None,
        instance=Session.objects.filter(pk=session_pk).first() or None,
        reporter=request.user
    )
    if request.POST and form.is_valid():
        session = form.save()

        return redirect("items:view", session.pk)
    context = {
        "form": form
    }

    return render(request, 'items/form.html', context)


def view_session(request, session_pk):
    session = get_object_or_404(Session, pk=session_pk)
    notes_form = SessionNoteForm(request.POST or None, instance=session)
    if request.POST and notes_form.is_valid():
        notes_form.save()

    return render(request, "items/view.html", {
        "session": session,
        "notes_form": notes_form
    })


def list_sessions(request):
    return render(request, "items/list.html", {
        'sessions': Session.objects.all().order_by("-start_time"),
    })
