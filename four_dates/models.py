from django.db import models


# Create your models here.
class Country(models.Model):
    alpha_2_code = models.CharField(max_length=2)
    alpha_3_code = models.CharField(max_length=3)
    name = models.CharField(max_length=50)


class SubRegionUnit(models.Model):
    name = models.CharField(max_length=50)


class SubRegion(models.Model):
    name = models.CharField(max_length=50)

    country = models.ForeignKey('Country', null=True, on_delete=models.CASCADE)

    agro_eco_zone = models.CharField(max_length=200, null=True)
    sub_region_unit = models.ForeignKey('SubRegionUnit', null=True, on_delete=models.CASCADE)
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)


class Crop(models.Model):
    name = models.CharField(max_length=50)


class FourDates(models.Model):
    name = models.CharField(max_length=100, null=True)
    sub_region = models.ForeignKey('SubRegion', on_delete=models.CASCADE)
    crop = models.ForeignKey('Crop', on_delete=models.CASCADE)

    source_file = models.CharField(max_length=20, null=True)

    plant_start = models.IntegerField(null=True)
    plant_end = models.IntegerField(null=True)
    harvest_start = models.IntegerField(null=True)
    harvest_end = models.IntegerField(null=True)

    flag = models.BooleanField(default=False)

