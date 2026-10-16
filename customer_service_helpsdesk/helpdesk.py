from django.shortcuts import render

def helpdesk_page(request):
    return render(request, 'helpdesk.html')