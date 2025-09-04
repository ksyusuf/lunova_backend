from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('zoom/', include('zoom.urls')),
    path('appointments/', include('appointments.urls')),
    path('forms/', include('forms.urls')),
]
