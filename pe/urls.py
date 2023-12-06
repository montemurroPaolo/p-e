# plotly_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pe_app.urls')),
    path('mydashapp/', include('mydashapp.urls')),
]
