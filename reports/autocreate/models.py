from django.db import models


class CompanyINN(models.Model):
    inn = models.CharField(max_length=250)

class CompanyReport(models.Model):
    inn = models.ForeignKey(CompanyINN, on_delete=models.CASCADE)
    report = models.FileField(upload_to='reports/%Y/%m/%d')

    