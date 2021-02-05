from django.shortcuts import render, redirect
from .forms import CompanyINNForm


def inn_create(request):
    if request.method == 'POST':
        company_form = CompanyINNForm(request.POST)
        if company_form.is_valid():
            company_form.save()
            return redirect('inn_create')
    else:
        company_form = CompanyINNForm()
        
    return render(request, 'inn_create.html', {'form': company_form})
