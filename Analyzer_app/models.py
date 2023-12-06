# plotly_app/models.py
from django.db import models

class Sale(models.Model):
    date = models.DateField()
    amount = models.FloatField()
    product = models.CharField(max_length=100)
