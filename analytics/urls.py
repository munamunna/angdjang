from django.urls import path
from .views import *
   


urlpatterns = [
    path('api/total-visitors/', TotalVisitorsView.as_view()),
    path('api/busiest-day/', BusiestDayView.as_view()),
    path('api/busiest-hour/', BusiestHourView.as_view()),
    path('api/busiest-section/', BusiestSectionView.as_view()),
    path('api/daily-trend/', DailyTrendView.as_view()),
    path('api/report-types/', ReportTypeListView.as_view()),
    path('api/floor-names/', FloorListView.as_view()),
   
]
