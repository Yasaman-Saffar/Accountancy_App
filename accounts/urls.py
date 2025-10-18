from django.urls import path
from . import views

urlpatterns = [
    path('add_new_group', views.add_new_group, name='add_new_group')
]