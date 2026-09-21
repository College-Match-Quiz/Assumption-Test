from django.db import models

class College(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    setting = models.CharField(max_length=50)
    class_size_avg = models.IntegerField()
    party_score = models.IntegerField(default=5)
    tuition_in_state = models.IntegerField()
    tuition_out_state = models.IntegerField()
    transfer_friendly = models.BooleanField(default=False)

    def __str__(self):
        return self.name