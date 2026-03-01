from django.urls import path
from . import views

urlpatterns = [
    # General Navigation
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('signup/', views.register, name='signup_unified'),
    
    # Add this line to fix the NoReverseMatch for 'recruiter'
    path('recruiter-login/', views.CustomLoginView.as_view(), name='recruiter'),
    
    # Candidate Workspace
    path('ats-checker/', views.home_ats_checker, name='home_ats_checker'),
    path('candidate-portal/', views.home_ats_checker, name='candidate'), 
    
    # Recruiter Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-room/', views.create_room, name='create_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    
    # Room & Analytics
    path('room/<slug:slug>/', views.room_detail, name='room_detail'),
    path('compare/<int:submission_id>/', views.compare_skills, name='compare_skills'),
    path('export-excel/', views.export_to_excel, name='export_to_excel'),
]