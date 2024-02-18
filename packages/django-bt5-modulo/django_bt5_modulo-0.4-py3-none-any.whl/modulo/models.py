from django.db import models
from django.urls import reverse


# Create your models here.


class TestData(models.Model):
    name = models.CharField(max_length=50)
    is_enable = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('modulo:success', kwargs={'pk': self.pk})
