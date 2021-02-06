from django import forms
from .models import Company


class CompanyINNForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('inn', )