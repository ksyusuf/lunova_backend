from rest_framework import viewsets, permissions, status, mixins, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import WeeklyAvailability, AvailabilityException
from .serializers import (
    WeeklyAvailabilitySerializer,
    AvailabilityExceptionSerializer,
    AvailabilityExceptionDeleteSerializer
)
from .permissions import IsExpertPermission, IsAvailabilityOwnerPermission, IsExpertOrAuthenticatedReadOnly
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import ExpertProfile
from django.db import transaction


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


class WeeklyAvailabilityView(generics.GenericAPIView):
    """
    Uzmanın haftalık uygunluklarını getirir veya topluca günceller.
    """
    permission_classes = [IsExpertPermission]
    serializer_class = WeeklyAvailabilitySerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'expertprofile'):
            raise ValidationError("Kullanıcının bir uzman profili yok.")
        return WeeklyAvailability.objects.filter(expert=user.expertprofile)

    def get(self, request):
        """Tüm mevcut weekly availabilities döner"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    def put(self, request):
            user = request.user
            expert = user.expertprofile
            incoming_data = request.data.get('availabilities', [])
            
            if not isinstance(incoming_data, list):
                return Response({'error': 'availabilities bir liste olmalıdır.'}, status=400)

            # Mevcut slotlar
            # İlişkilendirilmiş service nesnesini de çekiyoruz.
            existing_slots = list(WeeklyAvailability.objects.filter(expert=expert).select_related('service'))
            
            # Güncellenecek veya silinecek mevcut slotların kimliklerini (ID) tutmak için
            slots_to_delete = set()
            new_objects = []
            updated_objects = []

            def merge_slot(existing_slot, new_start, new_end):
                """
                Mevcut slot ile gelen slot saatlerini birleştirir.
                Ardışık veya çakışan saatleri tek slot hâline getirir.
                """
                if new_start < existing_slot.start_time:
                    existing_slot.start_time = new_start
                if new_end > existing_slot.end_time:
                    existing_slot.end_time = new_end
                return existing_slot

            # 1. Gelen Veriyi İşle ve Çakışan Mevcut Slotları Topla/Birleştir
            for item in incoming_data:
                try:
                    serializer = self.get_serializer(data=item)
                    serializer.is_valid(raise_exception=True)
                    data = serializer.validated_data
                except Exception as e:
                    # Serializer hatası durumunda döngüden çıkıp hata döndürelim
                    return Response({'error': f'Geçersiz veri: {e}'}, status=400)

                new_start = data['start_time']
                new_end = data['end_time']
                service_id = data.get('service').id if data.get('service') else None
                day = data['day_of_week']
                
                # Tüm diğer özellikler (is_active, slot_minutes, capacity) de aynı olmalı
                slot_attrs = {
                    'day_of_week': day,
                    'service_id': service_id,
                    'is_active': data.get('is_active'),
                    'slot_minutes': data.get('slot_minutes'),
                    'capacity': data.get('capacity'),
                }
                
                # Aynı gün ve AYNI TİP (service, is_active, slot_minutes, capacity) için mevcut slotlar
                same_type_slots = [
                    slot for slot in existing_slots
                    if slot.day_of_week == day 
                    and slot.service_id == slot_attrs.get('service_id')
                    and slot.is_active == slot_attrs.get('is_active')
                    and slot.slot_minutes == slot_attrs.get('slot_minutes')
                    and slot.capacity == slot_attrs.get('capacity')
                ]

                # Birleştirme adaylarını tutacak set
                merge_candidates = []
                
                # Gelen slotun başlangıcı ve bitişi için potansiyel birleştirilmiş aralık
                current_merged_start = new_start
                current_merged_end = new_end
                
                # NOT: Bu döngüde 'existing_slots' listesi manipüle edildiği için 
                # birleştirilen slotları çıkarmak önemlidir.
                
                for slot in same_type_slots:
                    # Çakışan veya ardışık slotları bul
                    is_overlapping_or_adjacent = (
                        not (slot.end_time < current_merged_start or slot.start_time > current_merged_end)
                        or slot.end_time == current_merged_start
                        or slot.start_time == current_merged_end
                    )
                    
                    if is_overlapping_or_adjacent and slot.id not in slots_to_delete:
                        # Sadece henüz silinmek üzere işaretlenmemiş slotları birleştirme adayı olarak al
                        merge_candidates.append(slot)
                        # Yeni birleştirilmiş aralığı güncelle
                        current_merged_start = min(current_merged_start, slot.start_time)
                        current_merged_end = max(current_merged_end, slot.end_time)
                
                
                if merge_candidates:
                    # Bütün adayları birleştirecek, yeni/güncellenmiş tek bir slot oluştur
                    # En eski adayı güncelleyecek slot olarak seçelim (listede ilk bulduğumuz)
                    base_slot = merge_candidates[0]
                    
                    # Başlangıç ve bitişi en geniş aralığa ayarla
                    base_slot.start_time = current_merged_start
                    base_slot.end_time = current_merged_end
                    
                    # Diğer alanları güncelle
                    for field in ['is_active', 'slot_minutes', 'capacity']:
                        setattr(base_slot, field, data.get(field))

                    # Veritabanına kaydet
                    base_slot.save()
                    updated_objects.append(base_slot)
                    
                    # Birleşen diğer mevcut slotları silinmek üzere işaretle
                    for slot_to_delete in merge_candidates[1:]:
                        slots_to_delete.add(slot_to_delete.id)
                        # existing_slots listesinden de çıkaralım ki sonraki incoming itemlar tarafından tekrar işlenmesin
                        # NOT: list.remove(x) pahalı olabilir, ancak listenin boyutu çok büyük değilse kabul edilebilir.
                        # existing_slots.remove(slot_to_delete) # Bu satır karmaşıklığı artırabilir, 'if slot.id not in slots_to_delete' kontrolü yeterli.

                else:
                    # Çakışma veya ardışıklık yok, yeni slot ekle
                    new_wa = WeeklyAvailability.objects.create(expert=expert, **data)
                    new_objects.append(new_wa)
                    # existing_slots listesine de ekleyelim ki sonraki incoming itemlar için kontrol edilebilsin
                    existing_slots.append(new_wa) 

            # 2. Silinmek Üzere İşaretlenen Slotları Veritabanından Sil
            deleted_count = 0
            if slots_to_delete:
                # delete() metodu geri dönen tuple'da silinen nesne sayısını döndürür.
                # (silinen nesne sayısı, {model_adı: sayı})
                deleted_count, _ = WeeklyAvailability.objects.filter(id__in=list(slots_to_delete)).delete()
                
            # 3. Yanıtı Oluştur
            
            # Sadece *güncel* kalanları listele
            final_updated_objects = [obj for obj in updated_objects if obj.id not in slots_to_delete]
            
            # Güncel veriyi veritabanından yeniden çekmek en tutarlı sonucu verir.
            current_data = WeeklyAvailabilitySerializer(
                WeeklyAvailability.objects.filter(expert=expert), many=True
            ).data

            added_data = WeeklyAvailabilitySerializer(new_objects, many=True).data
            updated_data = WeeklyAvailabilitySerializer(final_updated_objects, many=True).data

            return Response({
                'added': added_data,
                'updated': updated_data,
                'deleted_count': deleted_count, 
                'current': current_data
            }, status=200)


    def delete(self, request):
        """
        Gelen availabilities listesine göre silme işlemi yapar.
        Eğer listede slot yoksa, hata döner.
        Ortaya bölme mantığı uygulanır.
        """
        user = request.user
        expert = user.expertprofile
        incoming = request.data.get('availabilities', [])
        
        print(incoming)

        if not isinstance(incoming, list) or not incoming:
            return Response({'error': 'availabilities bir liste olmalıdır ve boş olmamalıdır.'}, status=400)

        # Mevcut slotlar
        existing = list(WeeklyAvailability.objects.filter(expert=expert))
        deleted_objects = []

        with transaction.atomic(): # Atomik işlem kullanmak her zaman en iyisidir
            for item in incoming:
                # Her döngüde mevcut slotları veritabanından YENİDEN ÇEK
                # Bu, önceki silme/bölme işlemlerinde oluşan tüm değişiklikleri yakalar.
                existing = list(WeeklyAvailability.objects.filter(expert=expert))
                
                serializer = self.get_serializer(data=item)
                serializer.is_valid(raise_exception=True)
                data = serializer.validated_data

                del_start = data['start_time']
                del_end = data['end_time']
                service_id = data['service'].id if data.get('service') else None
                day = data['day_of_week']

                # Aynı gün ve aynı servis için mevcut slotlar
                same_day_slots = [
                    slot for slot in existing
                    if slot.day_of_week == day and (slot.service_id == service_id)
                ]

                for slot in same_day_slots:
                    # Çakışma yoksa atla
                    if slot.end_time <= del_start or slot.start_time >= del_end:
                        continue

                    # Slot tamamen silinmek istenen aralıkla kapsanıyorsa, direkt sil
                    if del_start <= slot.start_time and del_end >= slot.end_time:
                        slot.delete()
                        deleted_objects.append(slot)
                        existing.remove(slot)
                    # Slot ortadan kesiliyorsa, ikiye böl
                    elif del_start > slot.start_time and del_end < slot.end_time:
                        # İlk parça: slot.start_time -> del_start
                        slot1 = WeeklyAvailability.objects.create(
                            expert=slot.expert,
                            day_of_week=slot.day_of_week,
                            start_time=slot.start_time,
                            end_time=del_start,
                            service=slot.service,
                            is_active=slot.is_active,
                            slot_minutes=slot.slot_minutes,
                            capacity=slot.capacity
                        )
                        # İkinci parça: del_end -> slot.end_time
                        slot2 = WeeklyAvailability.objects.create(
                            expert=slot.expert,
                            day_of_week=slot.day_of_week,
                            start_time=del_end,
                            end_time=slot.end_time,
                            service=slot.service,
                            is_active=slot.is_active,
                            slot_minutes=slot.slot_minutes,
                            capacity=slot.capacity
                        )
                        slot.delete()
                        deleted_objects.append(slot)
                        existing.remove(slot)
                    # Slotun başı kesiliyorsa
                    elif del_start <= slot.start_time < del_end < slot.end_time:
                        slot.start_time = del_end
                        slot.save()
                        deleted_objects.append(slot)
                    # Slotun sonu kesiliyorsa
                    elif slot.start_time < del_start < slot.end_time <= del_end:
                        slot.end_time = del_start
                        slot.save()
                        deleted_objects.append(slot)

        deleted_data = WeeklyAvailabilitySerializer(deleted_objects, many=True).data

        return Response({
            'deleted_count': len(deleted_objects),
            'deleted': deleted_data,
            'current': WeeklyAvailabilitySerializer(
                WeeklyAvailability.objects.filter(expert=expert), many=True
            ).data
        }, status=200)


class AvailabilityExceptionView(generics.GenericAPIView):
    """
    Uzmanın istisnalarını getirir, oluşturur, günceller veya siler.
    """
    permission_classes = [IsExpertPermission]
    serializer_class = AvailabilityExceptionSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'expertprofile'):
            raise ValidationError("Kullanıcının bir uzman profili yok.")
        return AvailabilityException.objects.filter(expert=user.expertprofile)

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'DELETE':
            return AvailabilityExceptionDeleteSerializer
        return self.serializer_class

    def put(self, request):
        """
        ID varsa update, yoksa create yapar.
        """
        expert = request.user.expertprofile
        incoming = request.data.get('exceptions', [])

        if not isinstance(incoming, list):
            return Response({'error': 'exceptions bir liste olmalıdır.'}, status=400)

        created = []
        updated = []
        errors = []

        with transaction.atomic():
            for item in incoming:
                exc_id = item.get('id')

                if exc_id:  # UPDATE
                    try:
                        instance = AvailabilityException.objects.get(id=exc_id, expert=expert)
                    except AvailabilityException.DoesNotExist:
                        errors.append({
                            'id': exc_id,
                            'message': f'ID {exc_id} ile eşleşen bir kayıt bulunamadı.'
                        })
                        continue

                    serializer = self.get_serializer(instance, data=item, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        updated.append(serializer.data)
                    else:
                        errors.append({
                            'id': exc_id,
                            'message': 'Doğrulama hatası',
                            'details': serializer.errors
                        })

                else:  # CREATE
                    serializer = self.get_serializer(data=item)
                    if serializer.is_valid():
                        new_obj = serializer.save(expert=expert)
                        created.append(self.get_serializer(new_obj).data)
                    else:
                        errors.append({
                            'item': item,
                            'message': 'Doğrulama hatası',
                            'details': serializer.errors
                        })

        current_data = self.get_serializer(
            AvailabilityException.objects.filter(expert=expert), many=True
        ).data

        return Response({
            'created': created,
            'updated': updated,
            'errors': errors,
            'current': current_data
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        """
        Gelen exceptions listesindeki öğelerle tam eşleşen
        (id + date + start_time + end_time) istisnaları siler.
        """
        expert = request.user.expertprofile
        incoming = request.data.get('exceptions', [])

        if not isinstance(incoming, list) or not incoming:
            return Response({'error': 'exceptions bir liste olmalıdır ve boş olmamalıdır.'},
                            status=status.HTTP_400_BAD_REQUEST)

        deleted = []
        errors = []

        with transaction.atomic():
            for item in incoming:
                serializer = self.get_serializer(data=item)
                if not serializer.is_valid():
                    errors.append({
                        'item': item,
                        'message': 'Doğrulama hatası',
                        'details': serializer.errors
                    })
                    continue

                data = serializer.validated_data
                exc_id = data['id']
                delete_date = data['date']
                start_time = data['start_time']
                end_time = data['end_time']

                try:
                    qs = AvailabilityException.objects.filter(
                        id=exc_id,
                        expert=expert,
                        date=delete_date,
                        start_time=start_time,
                        end_time=end_time
                    )

                    if qs.exists():
                        deleted.extend(self.get_serializer(qs, many=True).data)
                        qs.delete()
                    else:
                        errors.append({
                            'id': exc_id,
                            'message': 'Eşleşen kayıt bulunamadı (id, tarih veya saat uyuşmuyor).'
                        })
                except Exception as e:
                    errors.append({'id': exc_id, 'message': str(e)})

        current_data = self.get_serializer(
            AvailabilityException.objects.filter(expert=expert), many=True
        ).data

        return Response({
            'deleted_count': len(deleted),
            'deleted': deleted,
            'errors': errors,
            'current': current_data
        }, status=status.HTTP_200_OK)


class ExpertAvailabilityView(generics.ListAPIView):
    """
    Get expert's availability summary (public access for clients)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WeeklyAvailabilitySerializer

    def get_queryset(self):
        expert_id = self.kwargs.get('expert_id')
        return WeeklyAvailability.objects.filter(
            expert__user_id=expert_id,
            is_active=True
        )


class MyAvailabilityView(generics.GenericAPIView):
    """
    Current expert's availability calendar (weekly + exceptions)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if the user has an expertprofile or clientprofile
        if hasattr(user, 'expertprofile'):
            expert = user.expertprofile
        elif hasattr(user, 'clientprofile'):
            # For clientprofile, check for expert_id in query params
            expert_user_id = request.query_params.get('expert_user_id')
            if not expert_user_id:
                return Response({'error': 'expert_user_id parametresi gereklidir.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                expert = ExpertProfile.objects.get(user_id=expert_user_id)
            except ExpertProfile.DoesNotExist:
                return Response({'error': 'Belirtilen expert_user_id ile eşleşen bir uzman bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Kullanıcı bir uzman veya müşteri profiline sahip değil.'}, status=status.HTTP_403_FORBIDDEN)

        # Tarih aralığı için parametreleri al
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            # 1. Tarih parametrelerini kontrol et ve ata
            if start_date_str and end_date_str:
                # Parametreler geldiyse, onları kullan
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                # Parametreler gelmediyse, varsayılan aralığı (5 gün öncesi, 5 gün sonrası) kullan
                today = datetime.today().date()
                start_date = today - timedelta(days=5)
                end_date = today + timedelta(days=5)

            # 2. start_date > end_date kontrolü
            if start_date > end_date:
                return Response({'error': 'Başlangıç tarihi bitiş tarihinden sonra olamaz.'}, status=status.HTTP_400_BAD_REQUEST)

        except ValueError:
            # Tarih formatı hatası
            return Response({'error': 'Tarih formatı YYYY-MM-DD olmalıdır.'}, status=status.HTTP_400_BAD_REQUEST)

        # Weekly availability (Haftalık uygunluk)
        weekly_availabilities = WeeklyAvailability.objects.filter(
            expert=expert,
            is_active=True
        )

        # Exceptions (İstisnalar) - Artık dinamik start_date ve end_date aralığını kullanıyor
        exceptions = AvailabilityException.objects.filter(
            expert=expert,
            date__range=[start_date, end_date] 
        )

        # Build calendar data
        calendar_data = []
        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            day_avail_list = weekly_availabilities.filter(day_of_week=day_of_week)
            day_exceptions = exceptions.filter(date=current_date) 

            day_data = {
                'date': current_date,
                'weekly_availability': WeeklyAvailabilitySerializer(day_avail_list, many=True).data,
                'exceptions': AvailabilityExceptionSerializer(day_exceptions, many=True).data,
                'is_available': True
            }

            # cancel exception varsa
            if day_exceptions.filter(exception_type='cancel').exists():
                day_data['is_available'] = False

            calendar_data.append(day_data)
            current_date += timedelta(days=1)

        return Response({
            'expert_user_id': expert.user.id,
            'start_date': start_date,
            'end_date': end_date,
            'calendar': calendar_data
        }, status=status.HTTP_200_OK)


class AvailableExpertsByCategoryView(generics.ListAPIView):
    """
    Belirli bir kategori (slug) ve tarih aralığına göre uygun uzmanları listeler.
    GET parametreleri: category (slug), start_date, end_date
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        category_slug = request.query_params.get('category')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not category_slug or not start_date or not end_date:
            return Response(
                {'error': 'category, start_date ve end_date parametreleri zorunludur.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Tarih formatı YYYY-MM-DD olmalıdır.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Tarihler ters girildiyse düzelt
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        experts = ExpertProfile.objects.filter(
            services__slug__iexact=category_slug,
            user__is_active=True
        ).distinct()

        results = []

        for expert in experts:
            weekly_availabilities = WeeklyAvailability.objects.filter(
                expert=expert, is_active=True
            )
            if not weekly_availabilities.exists():
                continue

            exceptions = AvailabilityException.objects.filter(
                expert=expert,
                date__range=[start_date, end_date]
            )

            has_any_available_day = False
            current_date = start_date

            while current_date <= end_date:
                day_of_week = current_date.weekday()
                day_avail_list = weekly_availabilities.filter(day_of_week=day_of_week)
                day_exceptions = exceptions.filter(date=current_date)

                # Günlük uygunlukları kontrol et
                for slot in day_avail_list:
                    slot_start = slot.start_time
                    slot_end = slot.end_time

                    # İptal istisnalarını kontrol et
                    cancel_exceptions = day_exceptions.filter(exception_type='cancel')
                    is_fully_cancelled = False

                    for cancel in cancel_exceptions:
                        cancel_start = cancel.start_time
                        cancel_end = cancel.end_time

                        # Eğer saat aralığı belirtilmişse, çakışmayı kontrol et
                        if cancel_start and cancel_end:
                            if cancel_start <= slot_start and cancel_end >= slot_end:
                                is_fully_cancelled = True
                                break
                        else:
                            # Saat aralığı belirtilmemişse, tüm günü iptal olarak kabul et
                            is_fully_cancelled = True
                            break

                    if not is_fully_cancelled:
                        has_any_available_day = True
                        break

                # Ekstra uygunlukları kontrol et
                add_exceptions = day_exceptions.filter(exception_type='add')
                if add_exceptions.exists():
                    has_any_available_day = True

                if has_any_available_day:
                    break

                current_date += timedelta(days=1)

            if has_any_available_day:
                results.append({
                    "expert_user_id": expert.user.id,
                    "name": expert.user.get_full_name(),
                    "photo": expert.photo.url if getattr(expert, 'photo', None) else None,
                    "about": expert.about or "",
                    "category": category_slug,  # basit referans, frontend için yeterli
                })

        return Response(results, status=status.HTTP_200_OK)
