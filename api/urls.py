from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),  
    path('candidate/<int:candidate_id>/', views.candidate_detail, name='candidate_detail'),
    path('scorecard/<int:candidate_id>/', views.generate_scorecard, name='generate_scorecard'),
    path('shortlist/<int:candidate_id>/', views.shortlist_candidate, name='shortlist_candidate'),
    path('create-sample-job/', views.create_sample_job, name='create_sample_job'),
]