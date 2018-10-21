from django.urls import path

from items.views import list_sessions, create_session, view_session

app_name = "items"
urlpatterns = [
    path('', list_sessions, name="list"),
    path('create/', create_session, name="create"),
    #path('<int:session_pk>/edit', create_edit_session, name="edit"),
    path('<int:session_pk>/view', view_session, name="view"),
]
