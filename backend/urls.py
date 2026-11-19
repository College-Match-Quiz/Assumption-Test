from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include

from customer_service_helpsdesk.helpdesk import helpdesk_page
from home.views import SignUpView, about_page, home_page, quiz_page, terms_page, universities_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home'),
    path('about/', about_page, name='about'),
    path('terms/', terms_page, name='terms'),
    path('contact/', helpdesk_page, name='contact'),
    path('login/', LoginView.as_view(template_name='login.html', next_page='/', redirect_authenticated_user=True), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('quiz/', quiz_page, name='quiz'),
    path('universities/', universities_page, name='universities'),
    path('api/', include('api.urls')),
]
