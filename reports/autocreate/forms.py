from django import forms
from .models import Company


class CompanyINNForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('inn', )
        widgets = {
            'inn': forms.TextInput(
                    attrs={
                            'class': 'form-control',
                            'placeholder': 'Введите ИНН одной компании, либо нескольких через запятую',
                            'aria-label': 'Введите ИНН одной компании, либо нескольких через запятую',
                            'aria-describedby': 'button-addon2'
                        }
                )    
        }
