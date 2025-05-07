from django.contrib import admin

# Register your models here.

from django.contrib.gis import admin as gis_admin
from .models import Ride, User

from django.contrib.gis.geos import Point
from django.contrib.gis.db import models as gis_models

admin.site.register(User)
admin.site.register(Ride)
