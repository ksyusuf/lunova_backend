from rest_framework import viewsets, permissions, status, mixins, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import WeeklyAvailability, AvailabilityException
from .serializers import (
    WeeklyAvailabilitySerializer, AvailabilityExceptionSerializer,
    BulkWeeklyAvailabilitySerializer, BulkAvailabilityExceptionSerializer
)
from .permissions import IsExpertPermission, IsAvailabilityOwnerPermission, IsExpertOrAuthenticatedReadOnly
from rest_framework.exceptions import ValidationError


class WeeklyAvailabilityViewSet(viewsets.GenericViewSet):
    """
    Weekly availability CRUD operations
    """
    permission_classes = [IsExpertOrAuthenticatedReadOnly]
    serializer_class = WeeklyAvailabilitySerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'expertprofile'):
            raise ValidationError("Kullanıcının bir uzman profili yok.")
        return WeeklyAvailability.objects.filter(expert=user.expertprofile)

    def perform_create(self, serializer):
        serializer.save(expert=self.request.user.expertprofile)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WeeklyAvailabilityDetailView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Weekly availability detail, update and delete operations
    """
    permission_classes = [IsExpertPermission, IsAvailabilityOwnerPermission]
    serializer_class = WeeklyAvailabilitySerializer

    def get_queryset(self):
        return WeeklyAvailability.objects.filter(expert=self.request.user.expertprofile)


class AvailabilityExceptionViewSet(viewsets.GenericViewSet):
    """
    Availability exceptions CRUD operations
    """
    permission_classes = [permissions.IsAuthenticated, IsExpertOrAuthenticatedReadOnly]
    serializer_class = AvailabilityExceptionSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'expertprofile'):
            raise ValidationError("Kullanıcının bir uzman profili yok.")
        return AvailabilityException.objects.filter(expert=user.expertprofile)

    def perform_create(self, serializer):
        serializer.save(expert=self.request.user.expertprofile)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvailabilityExceptionDetailView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Availability exception detail, update and delete operations
    """
    permission_classes = [IsExpertPermission, IsAvailabilityOwnerPermission]
    serializer_class = AvailabilityExceptionSerializer

    def get_queryset(self):
        return AvailabilityException.objects.filter(expert=self.request.user.expertprofile)


class BulkWeeklyAvailabilityView(generics.CreateAPIView):
    """
    Bulk create weekly availabilities
    """
    permission_classes = [IsExpertPermission]
    serializer_class = BulkWeeklyAvailabilitySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkAvailabilityExceptionView(generics.CreateAPIView):
    """
    Bulk create availability exceptions
    """
    permission_classes = [IsExpertPermission]
    serializer_class = BulkAvailabilityExceptionSerializer


class ExpertAvailabilityView(generics.ListAPIView):
    """
    Get expert's availability summary (public access for clients)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WeeklyAvailabilitySerializer

    def get_queryset(self):
        expert_id = self.kwargs.get('expert_id')
        return WeeklyAvailability.objects.filter(
            expert_id=expert_id,
            is_active=True
        )


class MyAvailabilityView(generics.ListAPIView):
    """
    Get current expert's availability
    """
    permission_classes = [IsExpertPermission]
    serializer_class = WeeklyAvailabilitySerializer

    def get_queryset(self):
        return WeeklyAvailability.objects.filter(
            expert=self.request.user.expertprofile,
            is_active=True
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def expert_availability_calendar(request, expert_id):
    """
    Get expert's availability for a specific date range
    """
    from datetime import datetime, timedelta
    from django.utils import timezone

    # Query parameters
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if not start_date or not end_date:
        return Response(
            {'error': 'start_date ve end_date parametreleri zorunludur'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Tarih formatı YYYY-MM-DD olmalıdır'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get weekly availabilities
    weekly_availabilities = WeeklyAvailability.objects.filter(
        expert_id=expert_id,
        is_active=True
    )

    # Get exceptions for the date range
    exceptions = AvailabilityException.objects.filter(
        expert_id=expert_id,
        date__range=[start_date, end_date]
    )

    # Build calendar data
    calendar_data = []
    current_date = start_date

    while current_date <= end_date:
        day_of_week = current_date.weekday()

        # Check if there's an exception for this date
        date_exceptions = exceptions.filter(date=current_date)

        # Get weekly availability for this day
        day_availability = weekly_availabilities.filter(day_of_week=day_of_week).first()

        day_data = {
            'date': current_date,
            'day_of_week': day_of_week,
            'day_name': WeeklyAvailability.Weekday(day_of_week).label,
            'weekly_availability': WeeklyAvailabilitySerializer(day_availability).data if day_availability else None,
            'exceptions': AvailabilityExceptionSerializer(date_exceptions, many=True).data,
            'is_available': True
        }

        # Check if day is cancelled
        cancel_exception = date_exceptions.filter(exception_type='cancel').first()
        if cancel_exception:
            day_data['is_available'] = False
            day_data['cancel_note'] = cancel_exception.note

        calendar_data.append(day_data)
        current_date += timedelta(days=1)

    return Response({
        'expert_id': expert_id,
        'start_date': start_date,
        'end_date': end_date,
        'calendar': calendar_data
    })
