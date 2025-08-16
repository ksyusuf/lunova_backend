from django.contrib import admin
from .models import Form, Question, QuestionOption, FormResponse, Answer


class QuestionOptionInline(admin.TabularInline):
    """Soru seçenekleri için inline admin"""
    model = QuestionOption
    extra = 1
    ordering = ['order']


class QuestionInline(admin.TabularInline):
    """Sorular için inline admin"""
    model = Question
    extra = 1
    ordering = ['order']
    inlines = [QuestionOptionInline]


class AnswerInline(admin.TabularInline):
    """Cevaplar için inline admin"""
    model = Answer
    extra = 0
    readonly_fields = ['question', 'text_answer', 'selected_options']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    """Form admin paneli"""
    list_display = ['title', 'is_active', 'created_at', 'question_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuestionInline]
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Soru Sayısı'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Soru admin paneli"""
    list_display = ['question_text', 'form', 'question_type', 'order', 'is_required']
    list_filter = ['question_type', 'is_required', 'form']
    search_fields = ['question_text', 'form__title']
    ordering = ['form', 'order']
    inlines = [QuestionOptionInline]


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    """Soru seçeneği admin paneli"""
    list_display = ['option_text', 'question', 'order']
    list_filter = ['question__form', 'question__question_type']
    search_fields = ['option_text', 'question__question_text']
    ordering = ['question', 'order']


@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    """Form cevabı admin paneli"""
    list_display = ['user', 'form', 'submitted_at']
    list_filter = ['submitted_at', 'form']
    search_fields = ['user__username', 'form__title']
    readonly_fields = ['submitted_at']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Cevap admin paneli"""
    list_display = ['form_response', 'question', 'answer_summary']
    list_filter = ['question__question_type', 'question__form']
    search_fields = ['question__question_text', 'form_response__user__username']
    readonly_fields = ['form_response', 'question', 'text_answer', 'selected_options']
    
    def answer_summary(self, obj):
        if obj.text_answer:
            return obj.text_answer[:50] + "..." if len(obj.text_answer) > 50 else obj.text_answer
        elif obj.selected_options.exists():
            options = [opt.option_text for opt in obj.selected_options.all()]
            return ", ".join(options)
        return "Cevap yok"
    
    answer_summary.short_description = 'Cevap Özeti'
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
