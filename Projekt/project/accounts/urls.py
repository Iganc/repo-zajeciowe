from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('account/', views.account, name='account'),
    path('account/edit/', views.account_edit, name='account_edit'),
    path('account/add/', views.add_account, name='add_account'),
]