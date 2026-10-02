from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import path, include, reverse_lazy
from django.views.generic import CreateView

from customer_service_helpsdesk.helpdesk import helpdesk_page
from home.views import home_page, about_page, quiz_page, terms_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home'),
    path('about/', about_page, name='about'),
    path('terms/', terms_page, name='terms'),
    path('contact/', helpdesk_page, name='contact'),
    path('login/', LoginView.as_view(template_name='login.html', next_page='/', redirect_authenticated_user=True), name='login'),
    path('signup/', CreateView.as_view(form_class=UserCreationForm, template_name='signup.html', success_url=reverse_lazy('login')), name='signup'),
    path('quiz/', quiz_page, name='quiz'),
    path('api/', include('api.urls')),
]
