from rest_framework import serializers
from .models import Form, Question, QuestionOption, FormResponse, Answer


class QuestionOptionSerializer(serializers.ModelSerializer):
    """Soru seçenekleri için serializer"""
    
    class Meta:
        model = QuestionOption
        fields = ['id', 'option_text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    """Sorular için serializer - seçenekleri de içerir"""
    options = QuestionOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'order', 'is_required', 'options']


class FormSerializer(serializers.ModelSerializer):
    """Form detayları için serializer - soruları da içerir"""
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'is_active', 'created_at', 'questions']


class FormListSerializer(serializers.ModelSerializer):
    """Form listesi için kısa serializer"""
    
    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'is_active', 'created_at']


class AnswerSubmitSerializer(serializers.Serializer):
    """Form cevaplarını göndermek için serializer"""
    question_id = serializers.IntegerField()
    text_answer = serializers.CharField(required=False, allow_blank=True)
    selected_option_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    def validate(self, data):
        """Cevap tipine göre validasyon"""
        question_id = data.get('question_id')
        text_answer = data.get('text_answer')
        selected_option_ids = data.get('selected_option_ids', [])
        
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise serializers.ValidationError(f"Question with id {question_id} does not exist")
        
        # Soru tipine göre validasyon
        if question.question_type == 'text':
            if not text_answer or text_answer.strip() == '':
                raise serializers.ValidationError("Text answer is required for text questions")
            if selected_option_ids:
                raise serializers.ValidationError("Text questions cannot have selected options")
        
        elif question.question_type in ['test', 'multiple_choice']:
            if not selected_option_ids:
                raise serializers.ValidationError("Selected options are required for choice questions")
            if text_answer:
                raise serializers.ValidationError("Choice questions cannot have text answers")
            
            # Seçilen seçeneklerin bu soruya ait olduğunu kontrol et
            valid_option_ids = question.options.values_list('id', flat=True)
            for option_id in selected_option_ids:
                if option_id not in valid_option_ids:
                    raise serializers.ValidationError(f"Invalid option id: {option_id}")
        
        return data


class FormSubmitSerializer(serializers.Serializer):
    """Form gönderimi için serializer"""
    form_id = serializers.IntegerField()
    answers = AnswerSubmitSerializer(many=True)
    
    def validate(self, data):
        """Form ve cevaplar için validasyon"""
        form_id = data.get('form_id')
        answers = data.get('answers', [])
        
        try:
            form = Form.objects.get(id=form_id, is_active=True)
        except Form.DoesNotExist:
            raise serializers.ValidationError(f"Active form with id {form_id} does not exist")
        
        # Formun zorunlu sorularının cevaplanıp cevaplanmadığını kontrol et
        required_questions = form.questions.filter(is_required=True)
        answered_question_ids = [answer['question_id'] for answer in answers]
        
        for question in required_questions:
            if question.id not in answered_question_ids:
                raise serializers.ValidationError(f"Required question {question.id} is not answered")
        
        # Her soru için sadece bir cevap olmalı
        question_ids = [answer['question_id'] for answer in answers]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError("Duplicate question answers are not allowed")
        
        return data


class FormResponseSerializer(serializers.ModelSerializer):
    """Form cevaplarını görüntülemek için serializer"""
    form = FormListSerializer(read_only=True)
    answers = serializers.SerializerMethodField()
    
    class Meta:
        model = FormResponse
        fields = ['id', 'form', 'submitted_at', 'answers']
    
    def get_answers(self, obj):
        """Cevap detaylarını getir"""
        answers = []
        for answer in obj.answers.all():
            answer_data = {
                'question_id': answer.question.id,
                'question_text': answer.question.question_text,
                'question_type': answer.question.question_type,
            }
            
            if answer.text_answer:
                answer_data['text_answer'] = answer.text_answer
            elif answer.selected_options.exists():
                answer_data['selected_options'] = [
                    {'id': opt.id, 'text': opt.option_text} 
                    for opt in answer.selected_options.all()
                ]
            
            answers.append(answer_data)
        
        return answers
