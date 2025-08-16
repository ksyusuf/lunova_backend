from django.urls import path, include

urlpatterns = [
    path('accounts/', include('api.v1.accounts.urls')),  # 👈 v1/accounts
    # path('accounts/', include('accounts.urls')),  # 👈 önerilern -> accounts app'den direkt include

    path('zoom/', include('zoom.urls')),  # 👈 zoom app'den direkt include
    # path('experts/', include('api.v1.experts.urls')), gibi ileride genişletilir
    path('appointments/', include('appointments.urls')),  # 👈 appointments app'den direkt include
    path('forms/', include('forms.urls')),  # 👈 forms app'den direkt include
]
