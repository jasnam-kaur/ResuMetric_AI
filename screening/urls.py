from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-room/', views.create_room, name='create_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('ats-checker/', views.home_ats_checker, name='home_ats_checker'),
    path('room/<slug:slug>/', views.room_detail, name='room_detail'),
    path('export-excel/', views.export_to_excel, name='export_to_excel'),
    path('compare/<int:submission_id>/', views.compare_skills, name='compare_skills'),
]