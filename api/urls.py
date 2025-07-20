from django.urls import path, include

urlpatterns = [
    path('v1/', include('api.v1.urls')),  # 👈 versiyon 1 altında bütün yollar
    # ileride başka uygulamalar da eklenebilir:
    # path('experts/', include('api.v1.experts.urls')),
]
