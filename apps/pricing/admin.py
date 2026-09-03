from django.contrib import admin 
from .models import ScrapeJob, PriceSnapshot, PriceHistory 

admin.site.register(ScrapeJob) 
admin.site.register(PriceSnapshot) 
admin.site.register(PriceHistory)
