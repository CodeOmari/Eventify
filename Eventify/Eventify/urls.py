"""
URL configuration for Eventify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from main_app import views

from Eventify import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.events, name='events'),
    path('create/event', views.create_event, name='create_event'),
    path('event/<int:id>/', views.event_details, name='event_details'),
    path('event/<int:id>/ticket/', views.get_ticket, name='get_ticket'),

    path('events/search', views.search_event, name='search_event'),
    path('event/searched', views.search_event, name='search_event'),


    path('login', views.login_user, name='login'),
    path('logout', views.signout_user, name='logout'),
    path('register/', views.register, name='register'),

    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('reset-password-confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
