# Accountancy_App/Accountancy_App/scoreboard/urls.py
from django.urls import path
from . import views

app_name = "scoreboard"

urlpatterns = [
    # صفحه‌ی اصلی اسکربرد -> /scoreboard/
    path("", views.scoreboard, name="scoreboard"),
    # API برای داده‌های جدول -> /scoreboard/data/
    path("data/", views.scoreboard_data, name="scoreboard_data"),
]
