from django.db import models

class College(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    setting = models.CharField(max_length=50)
    class_size_avg = models.IntegerField(null=True, blank=True)
    party_score = models.IntegerField(default=5, null=True, blank=True)
    tuition_in_state = models.IntegerField(null=True, blank=True)
    tuition_out_state = models.IntegerField(null=True, blank=True)
    transfer_friendly = models.BooleanField(default=False)
    majors = models.TextField(blank=True, default='')  # comma-separated simple list
    residential_rate = models.IntegerField(null=True, blank=True)
    admit_rate = models.FloatField(null=True, blank=True)
    net_price_estimate = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name