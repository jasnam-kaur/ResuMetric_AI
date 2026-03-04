# project-level urls.py (in the core/ folder)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from screening.views import CustomLoginView, register, landing_page, dashboard, room_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root level authentication
    path('', landing_page, name='landing'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', register, name='register'),
    
    # ROOT LEVEL DASHBOARD FIX:
    # This line was crashing because 'dashboard' wasn't imported above
    path('dashboard/', dashboard, name='dashboard'), 
    path('room/<slug:slug>/', room_detail, name='room_detail'),
    # App-Specific Routes
    path('screening/', include('screening.urls')), 
    path('accounts/', include('django.contrib.auth.urls')),
]

# Serving media files correctly with document_root
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)