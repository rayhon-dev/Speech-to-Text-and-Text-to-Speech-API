from rest_framework import serializers
from .models import STTTranscription

class STTTranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = STTTranscription
        fields = [
            "id", "status", "text", "language", "model",
            "duration", "file_name", "file_size",
            "created_at", "updated_at", "error"
        ]
        read_only_fields = fields
