from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    role = models.CharField(max_length=200)
    phone = models.CharField(max_length=11)
    address = models.CharField(max_length=200)
    
    