from django.contrib import admin 
from .models import Airline, Airport, Route 

admin.site.register(Airline) 
admin.site.register(Airport) 
admin.site.register(Route)
