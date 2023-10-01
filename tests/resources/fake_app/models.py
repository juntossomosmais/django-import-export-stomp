from django.db import models


class FakeModel(models.Model):
    name = models.CharField(max_length=30)
    value = models.IntegerField(default=0)
