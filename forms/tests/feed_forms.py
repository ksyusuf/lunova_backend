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

from forms.models import Form, Question, QuestionOption, FormResponse, Answer
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
        description="Madde kullanımının risk seviyesini ölçmek için kullanılan test"
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
        Question.objects.create(
            form=form1,
            question_text=question_text,
            question_type='test',
            order=i,
            is_required=True
        )

    # Form 2: SDS (Esrar)
    form2 = Form.objects.create(
        title="SDS - Esrar Bağımlılık Şiddeti Ölçeği",
        description="Esrar bağımlılığının şiddetini ölçmek için kullanılan test"
    )

    sds_questions = [
        "Kullandığınız madde üzerinde kontrolünüzü kaybettiğinizi hissettiniz mi?",
        "Maddeyi bırakmayı düşündünüz mü?",
        "Madde kullanımı sizi zihinsel olarak meşgul etti mi?",
        "Maddeyi kullanmayı bırakamayacağınızı düşündünüz mü?",
        "Madde kullanımı size sıkıntı verdi mi?"
    ]

    for i, question_text in enumerate(sds_questions, start=1):
        Question.objects.create(
            form=form2,
            question_text=question_text,
            question_type='test',
            order=i,
            is_required=True
        )

    # Ekstra Form: Genel Sağlık Değerlendirme
    form3 = Form.objects.create(
        title="Genel Sağlık Değerlendirme Formu",
        description="Kullanıcıların genel sağlık durumlarını değerlendirmek için kullanılan form"
    )

    health_questions = [
        "Son 1 ay içinde fiziksel bir rahatsızlık yaşadınız mı?",
        "Uyku düzeninizde bir değişiklik oldu mu?",
        "Günlük aktivitelerinizi yerine getirirken zorlandınız mı?",
        "Son zamanlarda kendinizi stresli hissettiniz mi?",
        "Düzenli olarak egzersiz yapıyor musunuz?"
    ]

    for i, question_text in enumerate(health_questions, start=1):
        Question.objects.create(
            form=form3,
            question_text=question_text,
            question_type='multiple_choice' if i == 5 else 'text',
            order=i,
            is_required=False
        )

    # Kullanıcı yanıtlarını simüle et
    all_forms = [form1, form2, form3]
    for user in users:
        if random.random() < 0.8:  # %80 oranında doldurmuş gibi
            for form in all_forms:
                form_response = FormResponse.objects.create(
                    form=form,
                    user=user,
                    total_score=random.uniform(0, 10),
                    risk_level=random.choice(["Düşük", "Orta", "Yüksek"])
                )
                for question in form.questions.all():
                    if question.question_type == 'test':
                        Answer.objects.create(
                            form_response=form_response,
                            question=question,
                            text_answer=str(random.randint(0, 1))  # Evet (1) veya Hayır (0)
                        )
                    elif question.question_type == 'multiple_choice':
                        options = question.options.all()
                        if options.exists():  # Ensure options are not empty
                            selected_options = random.sample(list(options), k=random.randint(1, len(options)))
                            answer = Answer.objects.create(
                                form_response=form_response,
                                question=question
                            )
                            answer.selected_options.set(selected_options)
                    else:  # Text
                        Answer.objects.create(
                            form_response=form_response,
                            question=question,
                            text_answer="Örnek yanıt"
                        )

    print(
        f'Başarıyla {Form.objects.count()} form, {Question.objects.count()} soru ve {FormResponse.objects.count()} kullanıcı yanıtı oluşturuldu!'
    )


if __name__ == "__main__":
    create_sample_forms()
