from django.shortcuts import render
from django.db.models import Sum, Max
from django.db.models.functions import TruncDate, ExtractHour
from datetime import datetime, time, timedelta
from django.http import JsonResponse
from .models import Alert
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models.functions import TruncDate




def get_filtered_alerts(request):
    queryset = Alert.objects.all()

    start = request.GET.get('start')
    end = request.GET.get('end')
    floor = request.GET.get('floor_name')
    report_type = request.GET.get('report_type')
    # report_types = request.GET.getlist('report_type')

    if start and end:
        try:
            start_date = datetime.combine(parse_date(start), time.min)
            end_date = datetime.combine(parse_date(end), time.max)
        except Exception:
            return Alert.objects.none()
    else:
        today = datetime.today().date()
        start_date = datetime.combine(today - timedelta(days=6), time.min)
        end_date = datetime.combine(today, time.max)

    queryset = queryset.filter(alert_time__range=(start_date, end_date))

    if floor:
        queryset = queryset.filter(floor_name__iexact=floor)

    if report_type:
        queryset = queryset.filter(report_type__iexact=report_type)

    return queryset








#  1. Total Visitor Count
class TotalVisitorsView(APIView):
    def get(self, request):
        alerts = get_filtered_alerts(request)
        total = alerts.aggregate(total=Sum('incount'))['total'] or 0
        return Response({"total_visitor_count": total})



#  2. Busiest Day
class BusiestDayView(APIView):
    def get(self, request):
        alerts = get_filtered_alerts(request)
        data = (
            alerts.annotate(day=TruncDate('alert_time'))
            .values('day')
            .annotate(total=Sum('incount'))
            .order_by('-total')
            .first()
        )
        return Response({
            'busiest_day': data['day'] if data else None,
            'total_visitors': data['total'] if data else 0
        })



# 3. Busiest Hour
from datetime import datetime

class BusiestHourView(APIView):
    def get(self, request):
        alerts = get_filtered_alerts(request)
        data = (
            alerts.annotate(hour=ExtractHour('alert_time'))
            .values('hour')
            .annotate(total=Sum('incount'))
            .order_by('-total')
            .first()
        )

        if data:
            hour_24 = data['hour']
            # Convert to 12-hour format with AM/PM
            hour_display = datetime.strptime(str(hour_24), "%H").strftime("%I %p")
        else:
            hour_display = None

        return Response({
            'busiest_hour': hour_display,
            'total_visitors': data['total'] if data else 0
        })




# 4. Busiest Section (Floor with Max Occupancy)
class BusiestSectionView(APIView):
    def get(self, request):
        alerts = get_filtered_alerts(request)
        
        section = (
            alerts.values('section_name')
            .annotate(max_occ=Max('occupancy'))
            .order_by('-max_occ')
            .first()
        )

        return Response({
            'busiest_section': section['section_name'] if section else None,
            'occupancy': section['max_occ'] if section else 0
        })










class DailyTrendView(APIView):
    def get(self, request):
        alerts = Alert.objects.all()

        start = request.GET.get('start')
        end = request.GET.get('end')
        floor = request.GET.get('floor_name')
        report_type = request.GET.get('report_type')

        # Handle optional filtering
        if start and end:
            try:
                start_date = datetime.combine(parse_date(start), time.min)
                end_date = datetime.combine(parse_date(end), time.max)
            except:
                return Response({'error': 'Invalid date format'}, status=400)
        else:
            # Default to last 7 days (including today)
            today = datetime.today().date()
            start_date = datetime.combine(today - timedelta(days=6), time.min)
            end_date = datetime.combine(today, time.max)

        # Apply date range filter
        alerts = alerts.filter(alert_time__range=(start_date, end_date))

        # Optional floor and report_type filter
        if floor:
            alerts = alerts.filter(floor_name__iexact=floor)

        if report_type:
            alerts = alerts.filter(report_type__iexact=report_type)

        # Aggregate per day
        data = (
            alerts.annotate(day=TruncDate('alert_time'))
            .values('day')
            .annotate(total=Sum('incount'))
            .order_by('day')
        )

        trend = {entry['day'].strftime('%Y-%m-%d'): entry['total'] for entry in data}

        return Response({'daily_trend': trend})



#  6. Report Type List
class ReportTypeListView(APIView):
    def get(self, request):
        types = Alert.objects.values_list('report_type', flat=True).distinct()
        return Response({"report_types": list(types)})


class FloorListView(APIView):
    def get(self, request):
        floors = Alert.objects.values_list('floor_name', flat=True).distinct()
        return Response({"floors": list(floors)})









