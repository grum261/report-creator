from django.db import models


class Company(models.Model):
    inn = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    report_path = models.FilePathField()