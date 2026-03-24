from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.http import Http404

# Test views dla błędów 404 i 500
def test_404(request):
    """Test page dla 404"""
    raise Http404("Testowa strona 404")

def test_500(request):
    """Test page dla 500"""
    raise Exception("Testowy błąd 500 - test error handling")

# Custom error handlers
def handler_404(request, exception=None):
    """Obsługa błędu 404"""
    return render(request, '404.html', status=404)

def handler_500(request):
    """Obsługa błędu 500"""
    return render(request, '500.html', status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('transactions/', include('transactions.urls')),
    path('budgets/', include('budgets.urls')),
    
    # Test routes dla błędów
    path('test-404/', test_404, name='test_404'),
    path('test-500/', test_500, name='test_500'),
]

# Error handlers
handler404 = 'myProject.urls.handler_404'
handler500 = 'myProject.urls.handler_500'