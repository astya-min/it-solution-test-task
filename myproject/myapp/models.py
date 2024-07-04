from django.db import models


class GeneratedVideo(models.Model):
    text = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename