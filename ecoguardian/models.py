from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(models.Model):
  username = models.CharField(max_length=200, unique=True)
  password = models.CharField(max_length=25)
  is_admin = models.BooleanField()

  def __str__(self):
      return self.username

class IncidentCategory(models.Model):
  AIR_POLLUTION = 'Air Pollution'
  WATER_POLLUTION = 'Water Pollution'
  SOIL_POLLUTION = 'Soil Pollution'
  NOISE_POLLUTION = 'Noise Pollution'
  ANIMAL_ENDANGERMENT = 'Animal Endangerment'
  DISASTROUS_WEATHER = 'Disastrous Weather'
  OTHER = 'Other'

  CATEGORY_CHOICES = [
    (AIR_POLLUTION, 'Air Pollution'),
    (WATER_POLLUTION, 'Water Pollution'),
    (SOIL_POLLUTION, 'Soil Pollution'),
    (NOISE_POLLUTION, 'Noise Pollution'),
    (ANIMAL_ENDANGERMENT, 'Animal Endangerment'),
    (DISASTROUS_WEATHER, 'Disastrous Weather'),
    (OTHER, 'Other'),
  ]

  name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

  def __str__(self):
    return self.name
  
class IncidentReportStatus(models.TextChoices):
  NEW = 'New', _('New')
  IN_PROGRESS = 'In Progress', _('In Progress')
  RESOLVED = 'Resolved', _('Resolved')

class IncidentReport(models.Model):
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    incident_category = models.ForeignKey(IncidentCategory, on_delete=models.CASCADE)
    # evidence = models.FileField(upload_to='evidence/')
    user=models.CharField(max_length=255, default='Anonymous User')
    status = models.CharField(
        max_length=20,
        choices=IncidentReportStatus.choices,
        default=IncidentReportStatus.NEW
    )
    admin_description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.admin_description)
    
class Evidence(models.Model):
    incident_report = models.ForeignKey(IncidentReport, related_name='evidences', on_delete=models.CASCADE)
    file = models.FileField(upload_to='evidence/')
