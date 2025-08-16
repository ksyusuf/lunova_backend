from django.core.management.base import BaseCommand
from forms.models import Form, Question, QuestionOption


class Command(BaseCommand):
    help = 'Örnek form verileri oluşturur'

    def handle(self, *args, **options):
        self.stdout.write('Örnek form verileri oluşturuluyor...')
        
        # Mevcut formları temizle
        Form.objects.all().delete()
        
        # Form 1: Hasta Değerlendirme Formu
        form1 = Form.objects.create(
            title="Hasta Değerlendirme Formu",
            description="Hastaların genel durumunu değerlendirmek için kullanılan form"
        )
        
        # Form 1 - Soru 1 (Text)
        q1 = Question.objects.create(
            form=form1,
            question_text="Hangi şikayetlerle başvurdunuz? Lütfen detaylı olarak açıklayın.",
            question_type='text',
            order=1,
            is_required=True
        )
        
        # Form 1 - Soru 2 (Test)
        q2 = Question.objects.create(
            form=form1,
            question_text="Ağrı şiddetinizi nasıl değerlendirirsiniz?",
            question_type='test',
            order=2,
            is_required=True
        )
        
        # Form 1 - Soru 2 seçenekleri
        QuestionOption.objects.create(question=q2, option_text="Hiç ağrım yok", order=1)
        QuestionOption.objects.create(question=q2, option_text="Hafif ağrı", order=2)
        QuestionOption.objects.create(question=q2, option_text="Orta şiddette ağrı", order=3)
        QuestionOption.objects.create(question=q2, option_text="Şiddetli ağrı", order=4)
        QuestionOption.objects.create(question=q2, option_text="Dayanılmaz ağrı", order=5)
        
        # Form 1 - Soru 3 (Çok seçimli)
        q3 = Question.objects.create(
            form=form1,
            question_text="Hangi semptomları yaşıyorsunuz? (Birden fazla seçebilirsiniz)",
            question_type='multiple_choice',
            order=3,
            is_required=True
        )
        
        # Form 1 - Soru 3 seçenekleri
        QuestionOption.objects.create(question=q3, option_text="Baş ağrısı", order=1)
        QuestionOption.objects.create(question=q3, option_text="Mide bulantısı", order=2)
        QuestionOption.objects.create(question=q3, option_text="Baş dönmesi", order=3)
        QuestionOption.objects.create(question=q3, option_text="Yorgunluk", order=4)
        QuestionOption.objects.create(question=q3, option_text="Uykusuzluk", order=5)
        
        # Form 1 - Soru 4 (Text)
        q4 = Question.objects.create(
            form=form1,
            question_text="Daha önce benzer şikayetleriniz oldu mu? Varsa nasıl tedavi edildi?",
            question_type='text',
            order=4,
            is_required=False
        )
        
        # Form 2: Tedavi Takip Formu
        form2 = Form.objects.create(
            title="Tedavi Takip Formu",
            description="Tedavi sürecinin takibi için kullanılan form"
        )
        
        # Form 2 - Soru 1 (Test)
        q5 = Question.objects.create(
            form=form2,
            question_text="Tedaviye uyumunuzu nasıl değerlendirirsiniz?",
            question_type='test',
            order=1,
            is_required=True
        )
        
        # Form 2 - Soru 1 seçenekleri
        QuestionOption.objects.create(question=q5, option_text="Çok iyi", order=1)
        QuestionOption.objects.create(question=q5, option_text="İyi", order=2)
        QuestionOption.objects.create(question=q5, option_text="Orta", order=3)
        QuestionOption.objects.create(question=q5, option_text="Kötü", order=4)
        QuestionOption.objects.create(question=q5, option_text="Çok kötü", order=5)
        
        # Form 2 - Soru 2 (Text)
        q6 = Question.objects.create(
            form=form2,
            question_text="Tedavi sırasında herhangi bir yan etki yaşadınız mı?",
            question_type='text',
            order=2,
            is_required=False
        )
        
        # Form 2 - Soru 3 (Çok seçimli)
        q7 = Question.objects.create(
            form=form2,
            question_text="Hangi yaşam tarzı değişikliklerini yaptınız?",
            question_type='multiple_choice',
            order=3,
            is_required=False
        )
        
        # Form 2 - Soru 3 seçenekleri
        QuestionOption.objects.create(question=q7, option_text="Düzenli egzersiz", order=1)
        QuestionOption.objects.create(question=q7, option_text="Sağlıklı beslenme", order=2)
        QuestionOption.objects.create(question=q7, option_text="Sigara bırakma", order=3)
        QuestionOption.objects.create(question=q7, option_text="Alkol azaltma", order=4)
        QuestionOption.objects.create(question=q7, option_text="Stres yönetimi", order=5)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Başarıyla {Form.objects.count()} form, {Question.objects.count()} soru ve {QuestionOption.objects.count()} seçenek oluşturuldu!'
            )
        )
