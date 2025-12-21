from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .models import Form, FormResponse, Answer, Question, QuestionOption
from .serializers import (
    FormSerializer, FormListSerializer, FormSubmitSerializer, 
    FormResponseSerializer, QuestionSerializer, QuestionOptionSerializer
)

class FormListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Aktif formların listesini getir
        - Admin kullanıcılar tüm formları görebilir.
        - Diğer kullanıcılar yalnızca aktif formları görebilir.
        """
        if request.user.is_staff:  # Admin kullanıcılar
            forms = Form.objects.all()
        else:  # Normal kullanıcılar
            forms = Form.objects.filter(is_active=True)

        serializer = FormListSerializer(forms, many=True)
        return Response(serializer.data)

class FormDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, form_id):
        """
        Belirli bir formun detaylarını, sorularını ve seçeneklerini getir
        """
        form = get_object_or_404(Form, id=form_id, is_active=True)
        has_responded = FormResponse.objects.filter(form=form, user=request.user).exists()

        # Form detaylarını serialize et
        form_serializer = FormSerializer(form)
        response_data = form_serializer.data
        response_data['has_responded'] = has_responded

        # Soruları ve seçenekleri ekle
        questions = Question.objects.filter(form=form)
        question_serializer = QuestionSerializer(questions, many=True)
        response_data['questions'] = question_serializer.data

        for question in response_data['questions']:
            options_qs = QuestionOption.objects.filter(question_id=question['id'])
            option_serializer = QuestionOptionSerializer(options_qs, many=True)
            # keep raw options for compatibility
            question['options'] = option_serializer.data

            # Build a `possible_answers` field depending on question type:
            q_type = question.get('question_type')
            if q_type == 'multiple_choice':
                # return option id + text for clients to render checkboxes/radios
                question['possible_answers'] = [
                    {'id': opt.get('id'), 'text': opt.get('option_text')}
                    for opt in option_serializer.data
                ]
            elif q_type == 'test':
                # If explicit options exist (e.g. A/B/C/D), return them; otherwise
                # provide a default binary mapping (Evet/Hayır) commonly used in tests.
                if option_serializer.data:
                    question['possible_answers'] = [
                        {'id': opt.get('id'), 'text': opt.get('option_text')}
                        for opt in option_serializer.data
                    ]
                else:
                    question['possible_answers'] = [
                        {'value': 1, 'label': 'Evet'},
                        {'value': 0, 'label': 'Hayır'}
                    ]
            else:  # text or other open types
                # For text fields we provide a hint so the client knows free text is expected
                question['possible_answers'] = [
                    {'type': 'text', 'placeholder': question.get('placeholder', 'Cevabınızı yazınız...')}
                ]

        return Response(response_data)

class FormSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Form cevaplarını gönder
        """
        serializer = FormSubmitSerializer(data=request.data)
        if serializer.is_valid():
            form_id = serializer.validated_data['form_id']
            answers_data = serializer.validated_data['answers']

            if FormResponse.objects.filter(form_id=form_id, user=request.user).exists():
                return Response(
                    {'error': 'Bu formu zaten doldurdunuz'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                form_response = FormResponse.objects.create(
                    form_id=form_id,
                    user=request.user
                )

                for answer_data in answers_data:
                    question_id = answer_data['question_id']
                    text_answer = answer_data.get('text_answer', '')
                    selected_option_ids = answer_data.get('selected_option_ids', [])

                    answer = Answer.objects.create(
                        form_response=form_response,
                        question_id=question_id,
                        text_answer=text_answer
                    )

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

class UserResponsesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Kullanıcının doldurduğu formları getir
        """
        responses = FormResponse.objects.filter(user=request.user)
        serializer = FormResponseSerializer(responses, many=True)
        return Response(serializer.data)

class FormResponseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, response_id):
        """
        Belirli bir form cevabının detaylarını getir
        """
        response = get_object_or_404(FormResponse, id=response_id, user=request.user)
        serializer = FormResponseSerializer(response)
        return Response(serializer.data)

class IsAdminUserPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'

