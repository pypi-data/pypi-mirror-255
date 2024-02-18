from django.db import models

# Create your models here.

class Setting(models.Model):
    """Keyword and Values accessible Sitewide"""

    keyword = models.CharField(max_length=255, unique=True) 
    value = models.CharField(max_length=255)

    class Meta:
        """Meta for the Modes of Entry"""

        managed = True
        db_table = "setting"
