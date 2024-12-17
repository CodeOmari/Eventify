from django.contrib import admin

from main_app.models import Events, Registration, Payments

# Register your models here.

admin.site.register(Events)

admin.site.register(Registration)

admin.site.register(Payments)

admin.site.site_header = 'Eventify Administration'

admin.site.site_title = 'Eventify Administration'
