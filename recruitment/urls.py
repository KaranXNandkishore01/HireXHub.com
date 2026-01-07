from django.urls import path
from . import views
from django.http import JsonResponse


urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/hr/', views.hr_dashboard, name='hr_dashboard'),
    path('dashboard/applicant/', views.applicant_dashboard, name='applicant_dashboard'),
    path('company/create/', views.create_company, name='create_company'),
    path('post-job/', views.post_job, name='post_job'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/applicants/', views.view_applicants, name='view_applicants'),
    path('application/<int:application_id>/status/<str:status>/', views.update_application_status, name='update_application_status'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('resume-scorer/', views.resume_scorer, name='resume_scorer'),
    
    # Service Pages
    path('services/smart-match/', views.smart_matching, name='smart_matching'),
    path('services/analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('services/security/', views.secure_recruiting, name='secure_recruiting'),
    path('health/', views.health_check, name='health_check'),
]
