from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    # navbar urls
    path("apply_inflation_interest/", views.apply_inflation_interest, name="apply_inflation_interest"),
    path("inflation_apply/", views.apply_inflation_view, name="apply_inflation"),
    path("interest_apply/", views.apply_interest_view, name="apply_interest"),
    path("reset_inflation/", views.reset_inflation, name="reset_inflation"),

    # login urls
    path('admin_or_user/', views.admin_or_user, name='admin_or_user'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('banker_login/', views.banker_login, name='banker_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path("banker-logout/", views.banker_logout, name="banker_logout"),
    
    path('entry_page/', views.Entry_page, name='Entry_page'),
    path('setting/', views.setting, name='setting'),
    path('competition/', views.Home, name='home'),
    
    path('step1_base/', views.setup_step1, name='setup_step1'),
    path('step2_questions/', views.setup_step2, name='setup_step2'),
    path('step3_items/', views.setup_step3, name='setup_step3'),
    path('step4_inflation/', views.setup_step4, name='setup_step4'),
]