from django.contrib import admin
from .models import tmp,user_info,currency,currency_rate

# Register your models here.
admin.site.register(tmp)
admin.site.register(user_info)
admin.site.register(currency)
admin.site.register(currency_rate)

