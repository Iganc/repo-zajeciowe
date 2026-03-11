from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('transaction/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transaction/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
]