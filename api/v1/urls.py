from django.urls import path, include

urlpatterns = [
    path('accounts/', include('api.v1.accounts.urls')),  # 👈 v1/accounts
    # path('experts/', include('api.v1.experts.urls')), gibi ileride genişletilir
]
