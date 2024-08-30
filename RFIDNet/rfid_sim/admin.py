from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin
from .models import Simulation, RFIDReader, ChipBuffer, Route

# Register your models here.

admin.site.register(Simulation)
admin.site.register(RFIDReader, LeafletGeoAdmin)
admin.site.register(ChipBuffer, LeafletGeoAdmin)
admin.site.register(Route, LeafletGeoAdmin)