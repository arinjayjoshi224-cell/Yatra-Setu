from django.urls import path
from . import views

urlpatterns = [
    path("", views.control_panel, name="control_panel"),
    path("start/", views.start_system, name="start_system"),
    path("stop/", views.stop_system, name="stop_system"),
    path("add-route/", views.add_route, name="add_route"),
    path("add-airline/", views.add_airline, name="add_airline"),
]