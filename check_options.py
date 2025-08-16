#!/usr/bin/env python3
import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunova_backend.settings')
django.setup()

from forms.models import Question, QuestionOption

print("🔍 Form Seçeneklerini Kontrol Ediyorum...")
print("=" * 50)

# Form 1 - Soru 2 (Test)
print("\n📝 Form 1 - Soru 2 (Test):")
try:
    q2 = Question.objects.get(id=2)
    print(f"Soru: {q2.question_text}")
    print("Seçenekler:")
    for opt in q2.options.all():
        print(f"  ID: {opt.id}, Text: {opt.option_text}")
except Question.DoesNotExist:
    print("❌ Soru 2 bulunamadı!")

# Form 1 - Soru 3 (Çok seçimli)
print("\n📝 Form 1 - Soru 3 (Çok seçimli):")
try:
    q3 = Question.objects.get(id=3)
    print(f"Soru: {q3.question_text}")
    print("Seçenekler:")
    for opt in q3.options.all():
        print(f"  ID: {opt.id}, Text: {opt.option_text}")
except Question.DoesNotExist:
    print("❌ Soru 3 bulunamadı!")

print("\n✅ Kontrol tamamlandı!")
