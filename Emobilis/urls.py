"""
URL configuration for Emobilis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from Emobilis import settings
from main_app import views

urlpatterns = [
    path('events/search', views.search_event, name='search_event'),
    path('event/searched', views.search_event, name='search_event'),
    path('login', views.login_user, name='login'),
    path('logout', views.signout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('get/ticket', views.get_ticket, name='get_ticket'),
    path('add/event', views.add_event, name='add_event'),
    path('events/', views.events, name='events'),
    path('', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
