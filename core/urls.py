from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from screening.views import CustomLoginView # Import your custom view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This connects your app-level URLs (screening/urls.py)
    path('', include('screening.urls')), 
    
    # Points to your custom login logic and the renamed login.html
    path('login/', CustomLoginView.as_view(), name='login'),
    
    # Required for the logout functionality in your base.html
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
]