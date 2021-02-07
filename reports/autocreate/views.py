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
        
    return render(request, 'inn_send_form.html', {'form': company_form, 'inns_table': [
        {'UL': [
            6663003127, 7708503727, 7736050003, 7452027843, 
            6658021579, 7725604637, 4401006984, 3016003718, 5053051872
        ]}, 
        {'IP': [
            561100409545, 366512608416, 666200351548, 771409116994,
            773173084809, 773400211252, 503115929542, 702100195003, 771902452360
        ]}
    ]})

def report_downloads(request):
    companies = generate_reports(request)

    return render(request, 'report_downloads.html', {'companies': companies})
