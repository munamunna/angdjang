from django.db import models

# Create your models here.
from django.db import models


class Alert(models.Model):
    alert_id = models.AutoField(primary_key=True)
    floor_name = models.CharField(max_length=100)
    section_name = models.CharField(max_length=100,blank=True)  # NEW FIELD
    alert_time = models.DateTimeField()
    report_type = models.CharField(max_length=50, default='people_count')
    incount = models.PositiveIntegerField()
    outcount = models.PositiveIntegerField()
    occupancy = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.floor_name} at {self.alert_time}"

