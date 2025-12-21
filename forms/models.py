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
    # Nullable scoring fields for forms that have scoring systems
    max_score = models.FloatField(null=True, blank=True, verbose_name="Maksimum Puan")
    min_score = models.FloatField(null=True, blank=True, verbose_name="Minimum Puan")
    scoring_type = models.CharField(
        max_length=20, 
        choices=[
            ('none', 'Puanlama Yok'),
            ('binary', 'Evet/Hayır (0-1)'),
            ('scale', 'Ölçek (0-4)'),
            ('weighted', 'Ağırlıklı'),
            ('custom', 'Özel')
        ], 
        default='none', 
        verbose_name="Puanlama Tipi"
    )
    
    class Meta:
        verbose_name = "Form"
        verbose_name_plural = "Formlar"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

    def calculate_risk_level(self, score):
        """Calculate risk level based on score and form type"""
        if self.scoring_type == 'none' or score is None:
            return None
        
        if self.title.upper().find('DAST') != -1:
            # DAST-10 scoring: 0-10 scale
            if score >= 9:
                return "Çok Yüksek Risk"
            elif score >= 6:
                return "Yüksek Risk"
            elif score >= 3:
                return "Orta Risk"
            elif score >= 1:
                return "Düşük Risk"
            else:
                return "Madde Kullanımı Yok veya Çok Düşük"
        
        elif self.title.upper().find('SDS') != -1:
            # SDS scoring: 0-4 scale per question, up to 20 total
            if score >= 8:
                return "Yüksek Bağımlılık Belirtisi"
            elif score >= 5:
                return "Orta Düzey Bağımlılık Belirtisi"
            else:
                return "Düşük Bağımlılık Belirtisi"
        
        return "Değerlendirilmedi"

class Question(models.Model):
    """Soru modeli - farklı tiplerde sorular"""
    QUESTION_TYPES = [
        ('text', 'Açık Uçlu (Text)'),
        ('yes_no', 'Evet/Hayır'),
        ('scale', 'Ölçek (0-4)'),
        ('single_choice', 'Tek Seçim (A/B/C/D)'),
        ('multiple_choice', 'Çok Seçimli'),
        ('number', 'Sayısal'),
        ('date', 'Tarih'),
        ('textarea', 'Uzun Metin'),
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
    # Additional fields for scale questions
    min_scale_value = models.FloatField(default=0.0, verbose_name="Minimum Ölçek Değeri")
    max_scale_value = models.FloatField(default=4.0, verbose_name="Maksimum Ölçek Değeri")
    scale_labels = models.JSONField(
        blank=True, null=True, 
        help_text="Ölçek etiketleri, örn: {'0': 'Hiçbir zaman', '1': 'Nadiren', '2': 'Bazen', '3': 'Sıklıkla', '4': 'Her zaman'}",
        verbose_name="Ölçek Etiketleri"
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
    # Scoring support for weighted questions
    score_value = models.FloatField(default=0.0, verbose_name="Puan Değeri")
    is_correct = models.BooleanField(default=False, verbose_name="Doğru Cevap mı?")
    
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
    risk_level = models.CharField(max_length=100, blank=True, verbose_name="Risk Seviyesi")
    # Enhanced scoring fields
    percentage_score = models.FloatField(null=True, blank=True, verbose_name="Yüzde Puan")
    interpretation = models.TextField(blank=True, verbose_name="Yorum")
    recommendations = models.TextField(blank=True, verbose_name="Öneriler")
    
    class Meta:
        verbose_name = "Form Cevabı"
        verbose_name_plural = "Form Cevapları"
        ordering = ['-submitted_at']
        unique_together = ['form', 'user']  # Bir kullanıcı bir formu sadece bir kez doldurabilir
    
    def __str__(self):
        return f"{self.user.username} - {self.form.title}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate risk level based on form type and score
        if self.form and self.total_score is not None:
            self.risk_level = self.form.calculate_risk_level(self.total_score)
            
            # Calculate percentage score
            if self.form.max_score and self.form.max_score > 0:
                self.percentage_score = (self.total_score / self.form.max_score) * 100
        
        super().save(*args, **kwargs)


class Answer(models.Model):
    """Cevap modeli - kullanıcıların sorulara verdiği cevaplar"""
    form_response = models.ForeignKey(FormResponse, on_delete=models.CASCADE, related_name='answers', verbose_name="Form Cevabı")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Soru")
    text_answer = models.TextField(blank=True, verbose_name="Metin Cevabı")
    numeric_answer = models.FloatField(null=True, blank=True, verbose_name="Sayısal Cevap")
    selected_options = models.ManyToManyField(QuestionOption, blank=True, verbose_name="Seçilen Seçenekler")
    # Scoring for individual answers
    answer_score = models.FloatField(default=0.0, verbose_name="Cevap Puanı")
    
    class Meta:
        verbose_name = "Cevap"
        verbose_name_plural = "Cevaplar"
        unique_together = ['form_response', 'question']  # Bir soruya sadece bir cevap verilebilir
    
    def __str__(self):
        if self.text_answer:
            return f"{self.question.question_text[:30]}... - {self.text_answer[:50]}..."
        elif self.numeric_answer is not None:
            return f"{self.question.question_text[:30]}... - {self.numeric_answer}"
        elif self.selected_options.exists():
            return f"{self.question.question_text[:30]}... - {', '.join([opt.option_text for opt in self.selected_options.all()])}"
        return f"{self.question.question_text[:30]}... - Cevap yok"
    
    def calculate_score(self):
        """Calculate score for this answer based on question type and selected options"""
        total_score = 0.0
        
        if self.question.question_type in ['yes_no', 'single_choice', 'multiple_choice']:
            # Calculate based on selected options
            for option in self.selected_options.all():
                total_score += option.score_value
        elif self.question.question_type == 'scale' and self.numeric_answer is not None:
            # For scale questions, the numeric answer itself might be the score
            total_score = self.numeric_answer
        elif self.question.question_type == 'number' and self.numeric_answer is not None:
            # For number questions, apply question weight
            total_score = self.numeric_answer * self.question.score_weight
        
        self.answer_score = total_score
        return total_score


class RiskLevelMapping(models.Model):
    """Risk seviyesi eşleştirmeleri - farklı form tipleri için"""
    form_type = models.CharField(max_length=50, verbose_name="Form Tipi")
    min_score = models.FloatField(verbose_name="Minimum Puan")
    max_score = models.FloatField(verbose_name="Maksimum Puan")
    risk_level = models.CharField(max_length=100, verbose_name="Risk Seviyesi")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    recommendations = models.TextField(blank=True, verbose_name="Öneriler")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    
    class Meta:
        verbose_name = "Risk Seviyesi Eşleştirmesi"
        verbose_name_plural = "Risk Seviyesi Eşleştirmeleri"
        ordering = ['form_type', 'min_score']
    
    def __str__(self):
        return f"{self.form_type}: {self.min_score}-{self.max_score} = {self.risk_level}"
