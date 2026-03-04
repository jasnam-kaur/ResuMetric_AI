from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('signup/', views.register, name='signup_unified'),
    
    path('recruiter-login/', views.CustomLoginView.as_view(), name='recruiter'),
    
    path('ats-checker/', views.home_ats_checker, name='home_ats_checker'),
    path('candidate-portal/', views.home_ats_checker, name='candidate'), 
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-room/', views.create_room, name='create_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    
    path('compare/<int:submission_id>/', views.compare_skills, name='compare_skills'),
    path('export-excel/', views.export_to_excel, name='export_to_excel'),
]