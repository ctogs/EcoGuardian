from . import views
from django.urls import path, include
from .views import IncidentReportDeleteView, IncidentReportDetailView, IncidentReportListView, IncidentReportView, UserIncidentReportListView, DownloadAllEvidenceView

app_name = "ecoguardian"

urlpatterns = [
    path('main/', views.MainView.as_view(), name = "mainpage"),
    path('incident_report/', IncidentReportView.as_view(), name='incident_report'),
    path('incident-reports-view/', IncidentReportListView.as_view(), name='incident_reports_view'),
    path('my-reports/', UserIncidentReportListView.as_view(), name='user_incident_reports'),
    path('incident-reports/<int:pk>/', IncidentReportDetailView.as_view(), name='incident_report_detail'),
    path('incident-reports/delete/<int:pk>/', IncidentReportDeleteView.as_view(), name='incident_report_delete'),
    path('report/<int:pk>/download-evidence/', DownloadAllEvidenceView.as_view(), name='download_all_evidence'),

    # path('incident-reports-view/', IncidentReportListView.as_view(), name='admin_description')
]