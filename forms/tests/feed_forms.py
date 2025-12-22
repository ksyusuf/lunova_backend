"""
Database seeding script for forms app with sample data and user responses
"""

import os
import sys
import random
import django

# Script nereden çalıştırılırsa çalışsın, proje kökünü bul
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # script dizini
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))  # 2 seviye yukarı backend
sys.path.insert(0, BACKEND_DIR)

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunova_backend.settings')  # settings.py konumuna göre değiştir
django.setup()

from forms.models import Form, Question, QuestionOption, FormResponse, Answer, RiskLevelMapping
from accounts.models import User


def create_sample_forms():
    """Örnek form verileri oluşturur ve kullanıcı yanıtlarını simüle eder"""
    print('Örnek form verileri ve kullanıcı yanıtları oluşturuluyor...')

    # Mevcut formları temizle
    Form.objects.all().delete()
    FormResponse.objects.all().delete()

    # Kullanıcıları veritabanından al
    users = User.objects.filter(role="client")

    # Form 1: DAST-10
    form1 = Form.objects.create(
        title="DAST-10 Madde Kullanımı Tarama Testi",
        description="Madde kullanımının risk seviyesini ölçmek için kullanılan test",
        max_score=10.0,
        min_score=0.0,
        scoring_type='binary',
        stage=1
    )

    dast_questions = [
        "Yasa dışı bir madde kullandınız mı? (esrar, eroin, met, ecstasy, kokain vb.)",
        "Reçeteli bir ilacı doktorun önerdiği dozun dışında kullandığınız oldu mu?",
        "Madde kullanımınız yüzünden aile, arkadaş veya iş çevrenizle sorun yaşadınız mı?",
        "Madde kullanımı nedeniyle bir şeyi yapmayı unuttunuz ya da ertelediniz mi?",
        "Madde kullanımı nedeniyle suçluluk, pişmanlık ya da utanç hissettiniz mi?",
        "Madde kullanımı nedeniyle tedavi ya da danışmanlık alma ihtiyacı hissettiniz mi?",
        "Madde kullanımı nedeniyle yasal bir sorun yaşadınız mı? (gözaltı, mahkeme, vs.)",
        "Maddeyi bırakmak istediniz ama başaramadınız mı?",
        "Çevrenizden biri madde kullanımınız hakkında endişesini dile getirdi mi?",
        "Madde kullanımı nedeniyle fiziksel ya da psikolojik sağlık sorunu yaşadınız mı?"
    ]

    for i, question_text in enumerate(dast_questions, start=1):
        question = Question.objects.create(
            form=form1,
            question_text=question_text,
            question_type='yes_no',
            order=i,
            is_required=True,
            score_weight=1.0
        )
        # Evet/Hayır seçenekleri
        QuestionOption.objects.create(
            question=question,
            option_text="Evet",
            order=1,
            score_value=1.0
        )
        QuestionOption.objects.create(
            question=question,
            option_text="Hayır",
            order=2,
            score_value=0.0
        )

    # Form 2: SDS (Esrar)
    form2 = Form.objects.create(
        title="SDS - Esrar Bağımlılık Şiddeti Ölçeği",
        description="Esrar bağımlılığının şiddetini ölçmek için kullanılan test",
        max_score=20.0,
        min_score=0.0,
        scoring_type='scale',
        stage=1
    )

    sds_questions = [
        "Kullandığınız madde üzerinde kontrolünüzü kaybettiğinizi hissettiniz mi?",
        "Maddeyi bırakmayı düşündünüz mü?",
        "Madde kullanımı sizi zihinsel olarak meşgul etti mi?",
        "Maddeyi kullanmayı bırakamayacağınızı düşündünüz mü?",
        "Madde kullanımı size sıkıntı verdi mi?"
    ]

    for i, question_text in enumerate(sds_questions, start=1):
        question = Question.objects.create(
            form=form2,
            question_text=question_text,
            question_type='scale',
            order=i,
            is_required=True,
            min_scale_value=0.0,
            max_scale_value=4.0,
            score_weight=1.0,
            scale_labels={'0': 'Hiçbir zaman', '1': 'Nadiren', '2': 'Bazen', '3': 'Sıklıkla', '4': 'Her zaman'}
        )

    # Ekstra Form: Genel Sağlık Değerlendirme
    form3 = Form.objects.create(
        title="Genel Sağlık Değerlendirme Formu",
        description="Kullanıcıların genel sağlık durumlarını değerlendirmek için kullanılan form",
        max_score=5.0,
        min_score=0.0,
        scoring_type='scale',
        stage=2
    )

    health_questions = [
        "Son 1 ay içinde fiziksel bir rahatsızlık yaşadınız mı?",
        "Uyku düzeninizde bir değişiklik oldu mu?",
        "Günlük aktivitelerinizi yerine getirirken zorlandınız mı?",
        "Son zamanlarda kendinizi stresli hissettiniz mi?",
        "Düzenli olarak egzersiz yapıyor musunuz?"
    ]

    for i, question_text in enumerate(health_questions, start=1):
        if i == 5:  # Egzersiz sorusu için çoktan seçmeli
            question = Question.objects.create(
                form=form3,
                question_text=question_text,
                question_type='single_choice',
                order=i,
                is_required=False
            )
            QuestionOption.objects.create(
                question=question,
                option_text="Evet, düzenli egzersiz yapıyorum",
                order=1,
                score_value=0.0
            )
            QuestionOption.objects.create(
                question=question,
                option_text="Hayır, düzenli egzersiz yapmıyorum",
                order=2,
                score_value=1.0
            )
        else:
            Question.objects.create(
                form=form3,
                question_text=question_text,
                question_type='yes_no',
                order=i,
                is_required=False,
                score_weight=1.0
            )

    # Risk seviyesi eşleştirmelerini oluştur
    RiskLevelMapping.objects.all().delete()
    
    # DAST risk seviyeleri
    RiskLevelMapping.objects.create(
        form_type="DAST-10",
        min_score=0,
        max_score=2,
        risk_level="Madde Kullanımı Yok veya Çok Düşük",
        description="Düşük risk seviyesi",
        recommendations="Herhangi bir tedavi gerekmemektedir."
    )
    RiskLevelMapping.objects.create(
        form_type="DAST-10",
        min_score=3,
        max_score=5,
        risk_level="Orta Risk",
        description="Orta seviye risk",
        recommendations="Düzenli takip önerilir."
    )
    RiskLevelMapping.objects.create(
        form_type="DAST-10",
        min_score=6,
        max_score=8,
        risk_level="Yüksek Risk",
        description="Yüksek risk seviyesi",
        recommendations="Profesyonel yardım alınması önerilir."
    )
    RiskLevelMapping.objects.create(
        form_type="DAST-10",
        min_score=9,
        max_score=10,
        risk_level="Çok Yüksek Risk",
        description="Çok yüksek risk seviyesi",
        recommendations="Acil profesyonel müdahale gerekli."
    )
    
    # SDS risk seviyeleri
    RiskLevelMapping.objects.create(
        form_type="SDS",
        min_score=0,
        max_score=4,
        risk_level="Düşük Bağımlılık Belirtisi",
        description="Düşük bağımlılık riski",
        recommendations="Düzenli takip yeterlidir."
    )
    RiskLevelMapping.objects.create(
        form_type="SDS",
        min_score=5,
        max_score=7,
        risk_level="Orta Düzey Bağımlılık Belirtisi",
        description="Orta seviye bağımlılık riski",
        recommendations="Danışmanlık hizmeti önerilir."
    )
    RiskLevelMapping.objects.create(
        form_type="SDS",
        min_score=8,
        max_score=20,
        risk_level="Yüksek Bağımlılık Belirtisi",
        description="Yüksek bağımlılık riski",
        recommendations="Uzman desteği gereklidir."
    )

    # Kullanıcı yanıtlarını simüle et
    all_forms = [form1, form2, form3]
    for user in users:
        if random.random() < 0.8:  # %80 oranında doldurmuş gibi
            for form in all_forms:
                total_score = 0.0
                form_response = FormResponse.objects.create(
                    form=form,
                    user=user
                )
                
                for question in form.questions.all():
                    answer = Answer.objects.create(
                        form_response=form_response,
                        question=question
                    )
                    
                    if question.question_type == 'yes_no':
                        # Evet/Hayır soruları için rastgele cevap
                        is_yes = random.choice([True, False])
                        answer.numeric_answer = 1.0 if is_yes else 0.0
                        
                        # İlgili seçeneği işaretle
                        if is_yes:
                            selected_option = question.options.filter(option_text="Evet").first()
                        else:
                            selected_option = question.options.filter(option_text="Hayır").first()
                        if selected_option:
                            answer.selected_options.add(selected_option)
                        
                        total_score += answer.numeric_answer or 0.0
                        
                    elif question.question_type == 'scale':
                        # Ölçek soruları için 0-4 arası rastgele değer
                        scale_value = random.uniform(0, 4)
                        answer.numeric_answer = round(scale_value, 1)
                        total_score += scale_value
                        
                    elif question.question_type == 'single_choice':
                        # Tek seçimli sorular için rastgele seçenek
                        options = list(question.options.all())
                        if options:
                            selected_option = random.choice(options)
                            answer.selected_options.add(selected_option)
                            total_score += selected_option.score_value or 0.0
                    
                    # Cevap puanını hesapla
                    answer.calculate_score()
                    answer.save()
                
                # Form toplam puanını güncelle
                form_response.total_score = total_score
                form_response.save()  # Bu save() metodu risk seviyesini otomatik hesaplayacak

    print(
        f'Başarıyla {Form.objects.count()} form, {Question.objects.count()} soru ve {FormResponse.objects.count()} kullanıcı yanıtı oluşturuldu!'
    )


if __name__ == "__main__":
    create_sample_forms()
