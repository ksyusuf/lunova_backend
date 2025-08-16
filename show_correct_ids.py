#!/usr/bin/env python3
import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunova_backend.settings')
django.setup()

from forms.models import Form, Question, QuestionOption

print("🔍 Doğru Seçenek ID'leri")
print("=" * 50)

# Form 1'i bul
form1 = Form.objects.get(id=1)
print(f"\n📋 Form: {form1.title}")
print(f"📝 Açıklama: {form1.description}")

# Tüm soruları ve seçeneklerini göster
for question in form1.questions.all():
    print(f"\n❓ Soru {question.id}: {question.question_text}")
    print(f"   Tip: {question.get_question_type_display()}")
    print(f"   Zorunlu: {'Evet' if question.is_required else 'Hayır'}")
    
    if question.question_type in ['test', 'multiple_choice']:
        print("   Seçenekler:")
        for option in question.options.all():
            print(f"     ID: {option.id} → {option.option_text}")
    else:
        print("   Tip: Metin girişi")

print("\n✅ Doğru request formatı:")
print("""
{
    "form_id": 1,
    "answers": [
        {
            "question_id": 1,
            "text_answer": "Baş ağrısı ve mide bulantısı yaşıyorum"
        },
        {
            "question_id": 2,
            "selected_option_ids": [3]
        },
        {
            "question_id": 3,
            "selected_option_ids": [6, 9, 10]
        },
        {
            "question_id": 4,
            "text_answer": "Evet, 2 yıl önce benzer şikayetlerim vardı."
        }
    ]
}
""")
