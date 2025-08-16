from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Form, FormResponse, Answer
from .serializers import (
    FormSerializer, FormListSerializer, FormSubmitSerializer, 
    FormResponseSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_forms_list(request):
    """
    Aktif formların listesini getir
    
    GET /api/v1/forms/
    """
    forms = Form.objects.filter(is_active=True)
    serializer = FormListSerializer(forms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_form_detail(request, form_id):
    """
    Belirli bir formun detaylarını ve sorularını getir
    
    GET /api/v1/forms/{form_id}/
    """
    form = get_object_or_404(Form, id=form_id, is_active=True)
    
    # Kullanıcının bu formu daha önce doldurup doldurmadığını kontrol et
    has_responded = FormResponse.objects.filter(form=form, user=request.user).exists()
    
    serializer = FormSerializer(form)
    response_data = serializer.data
    response_data['has_responded'] = has_responded
    
    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_form(request):
    """
    Form cevaplarını gönder
    
    POST /api/v1/forms/submit/
    {
        "form_id": 1,
        "answers": [
            {
                "question_id": 1,
                "text_answer": "Açık uçlu cevap"
            },
            {
                "question_id": 2,
                "selected_option_ids": [1, 3]
            }
        ]
    }
    """
    serializer = FormSubmitSerializer(data=request.data)
    if serializer.is_valid():
        form_id = serializer.validated_data['form_id']
        answers_data = serializer.validated_data['answers']
        
        # Kullanıcının bu formu daha önce doldurup doldurmadığını kontrol et
        if FormResponse.objects.filter(form_id=form_id, user=request.user).exists():
            return Response(
                {'error': 'Bu formu zaten doldurdunuz'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Form response oluştur
            form_response = FormResponse.objects.create(
                form_id=form_id,
                user=request.user
            )
            
            # Cevapları kaydet
            for answer_data in answers_data:
                question_id = answer_data['question_id']
                text_answer = answer_data.get('text_answer', '')
                selected_option_ids = answer_data.get('selected_option_ids', [])
                
                answer = Answer.objects.create(
                    form_response=form_response,
                    question_id=question_id,
                    text_answer=text_answer
                )
                
                # Seçilen seçenekleri ekle
                if selected_option_ids:
                    answer.selected_options.set(selected_option_ids)
            
            return Response(
                {'message': 'Form başarıyla gönderildi', 'response_id': form_response.id},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': f'Form gönderilirken hata oluştu: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_responses(request):
    """
    Kullanıcının doldurduğu formları getir
    
    GET /api/v1/forms/my-responses/
    """
    responses = FormResponse.objects.filter(user=request.user)
    serializer = FormResponseSerializer(responses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_form_response_detail(request, response_id):
    """
    Belirli bir form cevabının detaylarını getir
    
    GET /api/v1/forms/responses/{response_id}/
    """
    response = get_object_or_404(FormResponse, id=response_id, user=request.user)
    serializer = FormResponseSerializer(response)
    return Response(serializer.data)
