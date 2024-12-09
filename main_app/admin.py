from django.contrib import admin

from main_app.models import Events, Tickets

# Register your models here.

admin.site.register(Events)

admin.site.register(Tickets)

admin.site.site_header = 'Eventify Administration'

admin.site.site_title = 'Eventify Administration'