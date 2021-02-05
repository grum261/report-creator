from django.contrib import admin
from .models import CompanyINN, CompanyReport

@admin.register(CompanyINN)
class CompanyINNAdmin(admin.ModelAdmin):
    list_display = ('inn', )

@admin.register(CompanyReport)
class CompanyReportAdmin(admin.ModelAdmin):
    list_display = ('inn', 'report', )