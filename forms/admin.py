from django.contrib import admin
from .models import Form, Question, QuestionOption, FormResponse, Answer, RiskLevelMapping

# --- INLINES ---

class QuestionOptionInline(admin.TabularInline):
    """Adminler seçenekleri ve puan değerlerini yönetebilir."""
    model = QuestionOption
    extra = 1
    ordering = ['order']
    fields = ('option_text', 'score_value', 'is_correct', 'order')

class QuestionInline(admin.TabularInline):
    """Adminler form altındaki soruları yönetebilir."""
    model = Question
    extra = 1
    ordering = ['order']
    fields = ('question_text', 'question_type', 'order', 'is_required')

# --- ADMIN CLASSES ---

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    """
    Adminler form başlıklarını, açıklamalarını ve genel ayarlarını yönetir.
    """
    list_display = ['title', 'scoring_type', 'stage', 'is_active']
    list_filter = ['scoring_type', 'is_active', 'stage']
    search_fields = ['title']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Soru bazlı CRUD işlemleri yapılabilir.
    """
    list_display = ['question_text', 'form', 'question_type', 'order']
    list_filter = ['form', 'question_type']
    search_fields = ['question_text']
    inlines = [QuestionOptionInline]

@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    """
    Seçenek bazlı CRUD işlemleri yapılabilir.
    """
    list_display = ['option_text', 'question', 'score_value', 'order']
    list_filter = ['question__form']

@admin.register(RiskLevelMapping)
class RiskLevelMappingAdmin(admin.ModelAdmin):
    """
    Adminler hangi puan aralığının hangi riske denk geleceğini (formülleri) yönetebilir.
    Ancak bu eşleşmenin kime çarptığını göremezler.
    """
    list_display = ['form_type', 'min_score', 'max_score', 'risk_level', 'is_active']
    list_filter = ['form_type', 'is_active']

# --- GİZLİLİK KRİTİK ALANLAR (CEVAPLAR VE SONUÇLAR) ---

@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    """
    Admin sadece formun doldurulduğu bilgisini görür. 
    Puan, Risk Seviyesi, Yorum gibi alanlar tamamen gizlendi.
    """
    list_display = ['user', 'form', 'submitted_at'] # total_score ve risk_level ÇIKARILDI
    list_filter = ['form', 'submitted_at']
    search_fields = ['user__username', 'form__title']
    
    # Detay sayfasında sadece kimin ne zaman doldurduğu görünür.
    fields = ['user', 'form', 'submitted_at']
    readonly_fields = ['user', 'form', 'submitted_at']

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """
    Cevaplar tablosu admin panelinde hiç görünmez. 
    Bireysel cevaplar üzerinde CRUD yapılamaz, admin erişemez.
    """
    def has_module_permission(self, request):
        return False

    def has_view_permission(self, request, obj=None):
        return False