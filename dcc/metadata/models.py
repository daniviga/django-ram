from django.db import models
from django_countries.fields import CountryField


class Manufacturer(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=128, unique=True)
    country = CountryField()

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Decoder(models.Model):
    name = models.CharField(max_length=128, unique=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE)
    version = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return "{0} - {1}".format(self.manufacturer, self.name)
