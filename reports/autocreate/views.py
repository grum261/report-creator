from django.shortcuts import render, redirect
from .forms import CompanyINNForm
from .reports_service import generate_reports


def inn_send_form(request):
    if request.method == 'POST':
        company_form = CompanyINNForm(request.POST)
        if company_form.is_valid():
            return redirect('report_downloads')
    else:
        company_form = CompanyINNForm()
        
    return render(request, 'inn_send_form.html', {'form': company_form})

def report_downloads(request):
    companies = generate_reports(request)

    return render(request, 'report_downloads.html', {'companies': companies})