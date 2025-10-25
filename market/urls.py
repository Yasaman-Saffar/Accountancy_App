from django.urls import path
from . import views

app_name = 'market'
urlpatterns = [
    path('get_team_item_info/', views.get_team_item_info, name='get_team_item_info'),
    path('dealing_items/', views.dealing_items, name='dealing_items'),
]