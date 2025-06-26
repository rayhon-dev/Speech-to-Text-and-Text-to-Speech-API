import uuid
from django.db import models
from users.models import CustomUser


class TTSConversion(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    voice = models.CharField(max_length=50, default="nova")
    language = models.CharField(max_length=10, default="en")
    speed = models.FloatField(default=1.0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    duration = models.FloatField(null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    audio_file = models.FileField(upload_to='tts_audio/', null=True, blank=True)
    error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def audio_url(self):
        if self.audio_file:
            return f"/api/v1/tts/{self.id}/audio"
        return None
