from django.contrib import admin
from django.urls import path, include

from home.views import home_page, about_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home'),
    path('about/', about_page, name='about'),
    path('api/', include('api.urls')),
]