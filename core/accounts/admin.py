from django.contrib import admin
from .models import User, Location, BloodInventory, Request, Donation, Notification, SystemLog, GlobalSettings

admin.site.register(User)
admin.site.register(Location)
admin.site.register(BloodInventory)
admin.site.register(Request)
admin.site.register(Donation)
admin.site.register(Notification)
admin.site.register(SystemLog)
admin.site.register(GlobalSettings)