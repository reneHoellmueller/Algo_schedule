from django.contrib import admin
from .models import ShiftPreference, Dienstplan, Shift, Employee

# Register your models here.
admin.site.register(ShiftPreference)
admin.site.register(Dienstplan)
admin.site.register(Shift)
admin.site.register(Employee)
