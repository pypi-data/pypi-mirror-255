from django.db import models

# Create your models here.
from cities_light.abstract_models import (AbstractCity, AbstractRegion,
    AbstractCountry, AbstractSubRegion)
from cities_light.receivers import connect_default_signals


class Country(AbstractCountry):
    pass
connect_default_signals(Country)

class Region(AbstractRegion):
    pass
connect_default_signals(Region)

class SubRegion(AbstractSubRegion):
    pass
connect_default_signals(SubRegion)

class City(AbstractCity):
    timezone = models.CharField(max_length=40)
connect_default_signals(City)