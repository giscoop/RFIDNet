from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as geo_models


class User(AbstractUser):
    def __str__(self):
        return "User ID: " + str(self.id)

class Simulation(geo_models.Model):
    owner = geo_models.ForeignKey("User", on_delete=geo_models.CASCADE, related_name="owned_sims")
    run = geo_models.BooleanField(default=False)

    def __str__(self):
        return "Simulation ID: " + str(self.id)


class RFIDReader(geo_models.Model):
    RFID_CHOICES = [('Low Frequency', 'Low Frequency (2m)'), ('High Frequency', 'High Frequency (10m)'), ('Ultra High Frequency', 'Ultra High Frequency (100m)')]

    simulation = geo_models.ForeignKey("Simulation", on_delete=geo_models.CASCADE, related_name="readers")
    chip_class = geo_models.CharField(max_length=32, choices=RFID_CHOICES, default=RFID_CHOICES[0][0])
    chip_range = geo_models.FloatField()
    location = geo_models.PointField(srid=3857)
    latitude = geo_models.FloatField()
    longitude = geo_models.FloatField()
    route_count = geo_models.IntegerField(null=True)

    def get_latitude(self):
        return self.location.y

    def get_longitude(self):
        return self.location.x

    def __str__(self):
        return "Reader ID: " + str(self.id)


class ChipBuffer(geo_models.Model):
    simulation = geo_models.ForeignKey("Simulation", on_delete=geo_models.CASCADE, related_name="buffers")
    reader = geo_models.ForeignKey("RFIDReader", on_delete=geo_models.CASCADE, related_name="buffer")
    buffer = geo_models.PolygonField(srid=3857)

    def __str__(self):
        return "Buffer ID: " + str(self.id)


class Route(geo_models.Model):
    simulation = geo_models.ForeignKey("Simulation", on_delete=geo_models.CASCADE, related_name="routes")
    trip_geometry = geo_models.LineStringField(srid=3857)
    trip_distance = geo_models.FloatField()
    trip_time = geo_models.FloatField()

    def __str__(self):
        return "Route ID: " + str(self.id)
    