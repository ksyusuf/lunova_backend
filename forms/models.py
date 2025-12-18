from django.db import models
from django.conf import settings


class Form(models.Model):
    """Form modeli - kullanıcılara gösterilecek formlar"""
    title = models.CharField(max_length=200, verbose_name="Form Başlığı")
    description = models.TextField(blank=True, verbose_name="Form Açıklaması")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    instructions = models.TextField(blank=True, verbose_name="Talimatlar")
    disclaimer = models.TextField(blank=True, verbose_name="Etik Hatırlatma")
    stage = models.PositiveIntegerField(default=1, verbose_name="Aşama")
    
    class Meta:
        verbose_name = "Form"
        verbose_name_plural = "Formlar"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Question(models.Model):
    """Soru modeli - farklı tiplerde sorular"""
    QUESTION_TYPES = [
        ('text', 'Açık Uçlu (Text)'),
        ('test', 'Test (A/B/C/D)'),
        ('multiple_choice', 'Çok Seçimli'),
    ]
    
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='questions', verbose_name="Form")
    question_text = models.TextField(verbose_name="Soru Metni")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name="Soru Tipi")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")
    is_required = models.BooleanField(default=True, verbose_name="Zorunlu mu?")
    score_weight = models.FloatField(default=1.0, verbose_name="Puan Ağırlığı")
    next_question = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Sonraki Soru"
    )
    
    class Meta:
        verbose_name = "Soru"
        verbose_name_plural = "Sorular"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.form.title} - {self.question_text[:50]}..."


class QuestionOption(models.Model):
    """Soru seçenekleri - test ve çok seçimli sorular için"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name="Soru")
    option_text = models.CharField(max_length=200, verbose_name="Seçenek Metni")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")
    
    class Meta:
        verbose_name = "Soru Seçeneği"
        verbose_name_plural = "Soru Seçenekleri"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question.question_text[:30]}... - {self.option_text}"


class FormResponse(models.Model):
    """Form cevapları - kullanıcıların form doldurma kayıtları"""
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='responses', verbose_name="Form")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderilme Tarihi")
    total_score = models.FloatField(default=0.0, verbose_name="Toplam Puan")
    risk_level = models.CharField(max_length=50, blank=True, verbose_name="Risk Seviyesi")
    
    class Meta:
        verbose_name = "Form Cevabı"
        verbose_name_plural = "Form Cevapları"
        ordering = ['-submitted_at']
        unique_together = ['form', 'user']  # Bir kullanıcı bir formu sadece bir kez doldurabilir
    
    def __str__(self):
        return f"{self.user.username} - {self.form.title}"


class Answer(models.Model):
    """Cevap modeli - kullanıcıların sorulara verdiği cevaplar"""
    form_response = models.ForeignKey(FormResponse, on_delete=models.CASCADE, related_name='answers', verbose_name="Form Cevabı")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Soru")
    text_answer = models.TextField(blank=True, verbose_name="Metin Cevabı")
    selected_options = models.ManyToManyField(QuestionOption, blank=True, verbose_name="Seçilen Seçenekler")
    
    class Meta:
        verbose_name = "Cevap"
        verbose_name_plural = "Cevaplar"
        unique_together = ['form_response', 'question']  # Bir soruya sadece bir cevap verilebilir
    
    def __str__(self):
        if self.text_answer:
            return f"{self.question.question_text[:30]}... - {self.text_answer[:50]}..."
        elif self.selected_options.exists():
            return f"{self.question.question_text[:30]}... - {', '.join([opt.option_text for opt in self.selected_options.all()])}"
        return f"{self.question.question_text[:30]}... - Cevap yok"
