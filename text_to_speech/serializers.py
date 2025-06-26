from rest_framework import serializers
from .models import TTSConversion

class TTSConversionSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()

    class Meta:
        model = TTSConversion
        fields = [
            "id", "status", "text", "voice", "language", "speed",
            "duration", "file_size", "audio_url",
            "created_at", "updated_at", "error"
        ]
        read_only_fields = ["id", "status", "duration", "file_size", "audio_url", "created_at", "updated_at", "error"]

    def get_audio_url(self, obj):
        request = self.context.get("request")
        if obj.audio_file and request:
            return request.build_absolute_uri(obj.audio_url())
        return None
