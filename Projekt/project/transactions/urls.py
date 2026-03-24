from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_transaction, name='add_transaction'),
    path('<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
]