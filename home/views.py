from django.shortcuts import render

def home_page(request):
    return render(request, 'home_page.html')

def about_page(request):
    return render(request, 'about.html')

def quiz_page(request):
    return render(request, 'quiz.html')