import uuid
from django.db import models
from users.models import CustomUser


class STTTranscription(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='stt_audio/')
    text = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10, default="en")
    model = models.CharField(max_length=50, default="whisper-1")
    duration = models.FloatField(null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"STT {self.id} by {self.user.username}"
