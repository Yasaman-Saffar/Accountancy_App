from django.urls import path
from . import views

urlpatterns = [
    path('scoreboard', views.scoreboard, name='scoreboard')
]