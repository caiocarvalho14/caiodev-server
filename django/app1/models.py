from django.db import models

# Create your models here.

class cliques(models.Model):
    id = models.AutoField(primary_key=True)
    data = models.DateTimeField(auto_now_add=True)