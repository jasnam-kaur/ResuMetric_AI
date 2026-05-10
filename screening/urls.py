from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('signup/', views.register, name='signup_unified'),
    
    path('recruiter-login/', views.CustomLoginView.as_view(), name='recruiter'),

    path('profile-setup/', views.profile_setup, name='profile_setup'),
    path('recruiter-setup/', views.recruiter_profile_setup, name='recruiter_setup'),
    
    path('ats-checker/', views.home_ats_checker, name='home_ats_checker'),
    path('candidate-portal/', views.home_ats_checker, name='candidate'), 
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-room/', views.create_room, name='create_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('room/edit/<slug:slug>/', views.edit_room, name='edit_room'),
    
    path('compare/<int:submission_id>/', views.compare_skills, name='compare_skills'),
    path('export-excel/', views.export_to_excel, name='export_to_excel'),

    path('settings/', views.recruiter_settings_view, name='recruiter_settings'),
    path('settings/', views.recruiter_settings_view, name='recruiter_settings_view'),

    path('history/', views.candidate_history, name='candidate_history'),
    path('unlock/<int:submission_id>/', views.unlock_premium_features, name='unlock_premium_features'),

    path('bulk-update/', views.bulk_status_update, name='bulk_status_update'),

    path('find-matches/<int:submission_id>/', views.find_matches, name='find_matches'),
]