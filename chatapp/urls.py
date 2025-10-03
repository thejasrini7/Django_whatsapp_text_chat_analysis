from django.urls import path
from . import views

app_name = 'chatapp'
urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('react-dashboard/', views.react_dashboard, name='react_dashboard'),
    path('group-events/', views.group_events_page, name='group_events'),
    path('api/upload/', views.upload_file, name='upload_file'),
    path('api/delete-file/', views.delete_file, name='delete_file'),
    path('api/get-uploaded-files/', views.get_uploaded_files, name='get_uploaded_files'),
    path('api/get-groups/', views.get_groups, name='get_groups'),
    path('api/get-group-dates/', views.get_group_dates, name='get_group_dates'),
    path('api/summarize/', views.summarize, name='summarize'),
    path('api/group-events-analytics/', views.group_events_analytics, name='group_events_analytics'),
    path('api/group-events-logs/', views.group_events_logs, name='group_events_logs'),
    path('api/sentiment/', views.sentiment, name='sentiment'),
    path('api/activity/', views.activity_analysis, name='activity_analysis'),
    path('api/export/', views.export_data, name='export_data'),
    path('api/ask/', views.ask_question, name='ask_question'),
    path('api/get-example-questions/', views.get_example_questions, name='get_example_questions'),
    path('api/generate-study-report/', views.generate_study_report, name='generate_study_report'),
]