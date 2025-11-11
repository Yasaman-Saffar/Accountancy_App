from django.urls import path
from . import views

app_name = 'bank'
urlpatterns = [
    path('bank_home/', views.bank_home, name='bank_home'),
    path('get_team_info/', views.get_team_info, name='get_team_info'),
    path('buying_questions/', views.buying_questions, name='buying_questions'),
    path('trading_questions/', views.trading_questions, name='trading_questions'),
    path('receive_award/', views.receive_award, name='receive_award'),
]