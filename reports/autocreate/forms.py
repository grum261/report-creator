from django import forms
from .models import CompanyINN


class CompanyINNForm(forms.ModelForm):
    class Meta:
        model = CompanyINN
        fields = ['inn', ]