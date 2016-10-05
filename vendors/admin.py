from django.contrib import admin
from vendors.models import Naics, Pool, Vendors, SetAside, PoolPIID

admin.site.register(Naics)
admin.site.register(Vendors)
admin.site.register(Pool)
admin.site.register(SetAside)
admin.site.register(PoolPIID)
# Register your models here.
