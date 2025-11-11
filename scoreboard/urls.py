# Accountancy_App/Accountancy_App/scoreboard/urls.py
from django.urls import path
from . import views

app_name = "scoreboard"

urlpatterns = [
    # Main scoreboard page -> /scoreboard/
    path("", views.scoreboard, name="scoreboard"),
    # API endpoint for scoreboard table data -> /scoreboard/data/
    path("data/", views.scoreboard_data, name="scoreboard_data"),
]
