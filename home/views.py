from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

def home_page(request):
    return render(request, 'home_page.html')

def about_page(request):
    return render(request, 'about.html')

def terms_page(request):
    return render(request, 'terms_of_agreement.html')

def quiz_page(request):
    return render(request, 'quiz.html')

def universities_page(request):
    return render(request, 'universities.html')
                                                