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
from datetime import datetime, timedelta
from .models import ExpertProfile


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
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        # Response hazırlanıyor
        response_data = {
            'added': [
                {
                    'id': wa.id,
                    'service': wa.service.id,
                    'day_of_week': wa.day_of_week,
                    'start_time': str(wa.start_time),
                    'end_time': str(wa.end_time)
                } for wa in result['added']
            ],
            'skipped': [
                {
                    'service': wa['service'].id,
                    'day_of_week': wa['day_of_week'],
                    'start_time': str(wa['start_time']),
                    'end_time': str(wa['end_time'])
                } for wa in result['skipped']
            ]
        }

        return Response(response_data, status=status.HTTP_201_CREATED)



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


class MyAvailabilityView(generics.GenericAPIView):
    """
    Current expert's availability calendar (weekly + exceptions)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        if not hasattr(user, 'expertprofile'):
            return Response({'error': 'User is not an expert.'}, status=status.HTTP_403_FORBIDDEN)

        expert = user.expertprofile

        # Tarih aralığı
        today = datetime.today().date()
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else today
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else today + timedelta(days=6)
        except ValueError:
            return Response({'error': 'Tarih formatı YYYY-MM-DD olmalıdır.'}, status=status.HTTP_400_BAD_REQUEST)

        # Weekly availability
        weekly_availabilities = WeeklyAvailability.objects.filter(
            expert=expert,
            is_active=True
        )

        # Exceptions (son 7 gün)
        exception_start = today - timedelta(days=6)
        exceptions = AvailabilityException.objects.filter(
            expert=expert,
            date__range=[exception_start, today + timedelta(days=6)]
        )

        # Build calendar data
        calendar_data = []
        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            day_avail = weekly_availabilities.filter(day_of_week=day_of_week).first()
            day_exceptions = exceptions.filter(date=current_date)

            day_data = {
                'date': current_date,
                'weekly_availability': WeeklyAvailabilitySerializer(day_avail).data if day_avail else None,
                'exceptions': AvailabilityExceptionSerializer(day_exceptions, many=True).data,
                'is_available': True
            }

            # cancel exception varsa
            if day_exceptions.filter(exception_type='cancel').exists():
                day_data['is_available'] = False

            calendar_data.append(day_data)
            current_date += timedelta(days=1)

        return Response({
            'expert_id': expert.id,
            'start_date': start_date,
            'end_date': end_date,
            'calendar': calendar_data
        }, status=status.HTTP_200_OK)


class AvailableExpertsByCategoryView(generics.ListAPIView):
    """
    Belirli bir kategori ve tarih aralığına göre uygun uzmanları listele.
    GET parametreleri: category, start_date, end_date
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        category_name = request.query_params.get('category')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not category_name or not start_date or not end_date:
            return Response(
                {'error': 'category, start_date ve end_date parametreleri zorunludur.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Tarih formatı kontrolü
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Tarih formatı YYYY-MM-DD olmalıdır.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Uygun uzmanları bul
        experts = ExpertProfile.objects.filter(
            services__name__iexact=category_name,
            user__is_active=True
        ).distinct()

        available_experts = []

        for expert in experts:
            weekly_availabilities = WeeklyAvailability.objects.filter(
                expert=expert, is_active=True
            )

            if not weekly_availabilities.exists():
                continue  # hiç haftalık uygunluğu yok

            exceptions = AvailabilityException.objects.filter(
                expert=expert,
                date__range=[start_date, end_date]
            )

            # Tüm tarihleri sırayla kontrol et
            current_date = start_date
            is_fully_unavailable = True
            available_days = []

            while current_date <= end_date:
                day_of_week = current_date.weekday()
                day_avail = weekly_availabilities.filter(day_of_week=day_of_week).first()

                cancel_exception = exceptions.filter(
                    date=current_date, exception_type='cancel'
                ).first()

                if day_avail and not cancel_exception:
                    is_fully_unavailable = False
                    available_days.append(str(current_date))

                current_date += timedelta(days=1)

            if not is_fully_unavailable:
                available_experts.append({
                    'id': expert.id,
                    'name': expert.user.get_full_name(),
                    'category': expert.category.name if expert.category else None,
                    'about': expert.about or "",
                    'photo': expert.photo.url if getattr(expert, 'photo', None) else None,
                    'available_days': available_days,
                    'total_available_days': len(available_days)
                })

        return Response(available_experts, status=status.HTTP_200_OK)