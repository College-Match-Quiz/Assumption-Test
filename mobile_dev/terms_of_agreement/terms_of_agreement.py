from django.shortcuts import render

def terms_page(request):
    return render(request, 'terms_of_agreements.html')