from django.contrib import admin
from apple.models import Naics, Pool, Vendor, SetAside, PoolPIID

admin.site.register(Naics)
admin.site.register(Vendor)
admin.site.register(Pool)
admin.site.register(SetAside)
admin.site.register(PoolPIID)
# Register your models here.
