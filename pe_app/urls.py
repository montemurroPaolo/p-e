# plotly_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('getData', views.get_data, name='data'),
]
