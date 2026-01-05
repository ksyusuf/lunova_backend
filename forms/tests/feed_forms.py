"""
Optimized and null-safe database seeding script for Lunova forms app
"""

import os
import sys
import random
import django

# Proje kökünü bul ve sys.path'e ekle
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunova_backend.settings')
django.setup()

from django.db import transaction
from forms.models import Form, Question, QuestionOption, FormResponse, Answer, RiskLevelMapping
from accounts.models import User

def create_sample_forms():
    print(">>> Örnek veriler temizleniyor...")
    
    with transaction.atomic():
        # Veri temizliği (Cascade silme sayesinde ilişkili cevaplar da silinir)
        Form.objects.all().delete()
        RiskLevelMapping.objects.all().delete()

        users = User.objects.filter(role="client")
        if not users.exists():
            print("!!! HATA: Veritabanında 'client' rolüne sahip kullanıcı bulunamadı.")
            return

        # ---------- FORMLAR ----------
        form1 = Form.objects.create(
            title="DAST-10 Madde Kullanımı Tarama Testi",
            description="Madde kullanımının risk seviyesini ölçmek için kullanılan test",
            max_score=10.0, min_score=0.0,
            scoring_type='binary', stage=1
        )

        form2 = Form.objects.create(
            title="SDS - Esrar Bağımlılık Şiddeti Ölçeği",
            description="Esrar bağımlılığının şiddetini ölçmek için kullanılan test",
            max_score=20.0, min_score=0.0,
            scoring_type='scale', stage=1
        )

        form3 = Form.objects.create(
            title="Genel Sağlık Değerlendirme Formu",
            description="Kullanıcıların genel sağlık durumlarını değerlendirmek için form",
            max_score=5.0, min_score=0.0,
            scoring_type='scale', stage=2
        )

        # ---------- SORULAR ----------
        dast_questions_text = [
            "Yasa dışı bir madde kullandınız mı?",
            "Reçeteli bir ilacı doktorun önerdiği dozun dışında kullandınız mı?",
            "Madde kullanımınız yüzünden sosyal sorun yaşadınız mı?",
            "Madde kullanımı nedeniyle bir şeyi yapmayı unuttunuz mu?",
            "Madde kullanımı nedeniyle suçluluk hissettiniz mi?",
            "Madde kullanımı nedeniyle tedavi ihtiyacı hissettiniz mi?",
            "Madde kullanımı nedeniyle yasal bir sorun yaşadınız mı?",
            "Maddeyi bırakmak istediniz ama başaramadınız mı?",
            "Çevrenizden biri kullanımınız hakkında endişesini dile getirdi mi?",
            "Madde kullanımı nedeniyle sağlık sorunu yaşadınız mı?"
        ]

        sds_questions_text = [
            "Kullandığınız madde üzerinde kontrolünüzü kaybettiğinizi hissettiniz mi?",
            "Maddeyi bırakmayı düşündünüz mü?",
            "Madde kullanımı sizi zihinsel olarak meşgul etti mi?",
            "Maddeyi kullanmayı bırakamayacağınızı düşündünüz mü?",
            "Madde kullanımı size sıkıntı verdi mi?"
        ]

        health_questions_text = [
            "Son 1 ay içinde fiziksel bir rahatsızlık yaşadınız mı?",
            "Uyku düzeninizde bir değişiklik oldu mu?",
            "Günlük aktivitelerinizi yerine getirirken zorlandınız mı?",
            "Son zamanlarda kendinizi stresli hissettiniz mi?",
            "Düzenli olarak egzersiz yapıyor musunuz?"
        ]

        # Soruları Bulk Create Hazırlığı
        questions_to_create = []
        
        # Form 1 (DAST) - Binary
        for i, txt in enumerate(dast_questions_text, 1):
            questions_to_create.append(Question(form=form1, question_text=txt, question_type='yes_no', order=i))
        
        # Form 2 (SDS) - Scale
        for i, txt in enumerate(sds_questions_text, 1):
            questions_to_create.append(Question(
                form=form2, question_text=txt, question_type='scale', order=i,
                scale_labels={'0':'Hiç','1':'Az','2':'Orta','3':'Çok','4':'Her zaman'}
            ))
        
        # Form 3 (Health) - Mixed
        for i, txt in enumerate(health_questions_text, 1):
            q_type = 'single_choice' if "egzersiz" in txt.lower() else 'yes_no'
            questions_to_create.append(Question(form=form3, question_text=txt, question_type=q_type, order=i))

        created_questions = Question.objects.bulk_create(questions_to_create)

        # ---------- SEÇENEKLER (OPTIONS) ----------
        options_to_create = []
        for q in created_questions:
            if q.question_type == 'yes_no':
                options_to_create.append(QuestionOption(question=q, option_text="Evet", order=1, score_value=1.0))
                options_to_create.append(QuestionOption(question=q, option_text="Hayır", order=2, score_value=0.0))
            elif q.question_type == 'single_choice':
                options_to_create.append(QuestionOption(question=q, option_text="Evet, düzenli", order=1, score_value=0.0))
                options_to_create.append(QuestionOption(question=q, option_text="Hayır, düzensiz", order=2, score_value=1.0))

        QuestionOption.objects.bulk_create(options_to_create)

        # ---------- RISK MAPPINGS ----------
        RiskLevelMapping.objects.bulk_create([
            RiskLevelMapping(form_type="DAST-10", min_score=0, max_score=2, risk_level="Düşük Risk"),
            RiskLevelMapping(form_type="DAST-10", min_score=3, max_score=5, risk_level="Orta Risk"),
            RiskLevelMapping(form_type="DAST-10", min_score=6, max_score=10, risk_level="Yüksek Risk"),
            RiskLevelMapping(form_type="SDS", min_score=0, max_score=4, risk_level="Düşük Bağımlılık"),
            RiskLevelMapping(form_type="SDS", min_score=5, max_score=20, risk_level="Yüksek Bağımlılık"),
        ])

        # ---------- USER RESPONSES (SIMULATION) ----------
        print(">>> Kullanıcı yanıtları simüle ediliyor...")
        
        for user in users:
            if random.random() > 0.5:  # Her kullanıcı her formu doldurmasın
                for form in [form1, form2, form3]:
                    # FormResponse oluştur (save metodu risk_level hesaplar)
                    response = FormResponse.objects.create(form=form, user=user)
                    
                    total_score = 0.0
                    questions = form.questions.all()
                    
                    for q in questions:
                        ans_score = 0.0
                        numeric_val = None
                        
                        # Answer nesnesini oluştur
                        answer = Answer.objects.create(form_response=response, question=q)
                        
                        if q.question_type == 'yes_no' or q.question_type == 'single_choice':
                            opt = random.choice(q.options.all())
                            answer.selected_options.add(opt)
                            ans_score = opt.score_value
                        
                        elif q.question_type == 'scale':
                            numeric_val = float(random.randint(0, 4))
                            ans_score = numeric_val
                        
                        answer.numeric_answer = numeric_val
                        answer.answer_score = ans_score
                        answer.save()
                        total_score += ans_score
                    
                    # FormResponse'u güncelle (risk_level tetiklenmesi için tekrar save)
                    response.total_score = total_score
                    response.save()

    print(f">>> İşlem Tamamlandı!")
    print(f"Oluşturulan Form Sayısı: {Form.objects.count()}")
    print(f"Toplam Yanıt Sayısı: {FormResponse.objects.count()}")

if __name__ == "__main__":
    create_sample_forms()
