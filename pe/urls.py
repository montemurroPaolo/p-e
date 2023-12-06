# plotly_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pe_app.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    ]
