from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('transactions/', include('transactions.urls')),
    path('budgets/', include('budgets.urls')),
]