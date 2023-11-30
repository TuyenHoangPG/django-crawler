from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.model import TimeStampMixin


# Create your models here.
class Property(TimeStampMixin):
    property_id = models.CharField(max_length=255, null=False, default="")
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    images = ArrayField(
        models.CharField(max_length=255, null=True, blank=True),
        default=list,
        null=True,
    )
    address = models.CharField(max_length=255, null=False)
    area = models.FloatField(null=True)
    price = models.FloatField(null=True)
    bedrooms = models.IntegerField(default=0, null=True)
    furniture = models.CharField(max_length=50, null=True)
    bancony = models.CharField(max_length=50, null=True)
    direction = models.CharField(max_length=30, null=True)
    bathrooms = models.IntegerField(default=0, null=True)
    url = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = "property"
