from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class Number(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    number=models.CharField(max_length=100)


    def __str__(self):
        return f"{self.Number}"
    