from django.urls import path
from .views import report_page, report_data

urlpatterns = [
    path('report/', report_page, name='inventory_report'),
    path('api/report/', report_data, name='inventory_report_data'),
]
