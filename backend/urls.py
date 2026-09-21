from django.contrib import admin
from django.urls import path, include

from home.views import home_page, about_page, quiz_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home'),
    path('about/', about_page, name='about'),
    path('quiz/', quiz_page, name='quiz'),
    path('api/', include('api.urls')),
]