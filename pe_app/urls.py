# plotly_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dash_page/', views.dash_page, name='dash_page'),
]
