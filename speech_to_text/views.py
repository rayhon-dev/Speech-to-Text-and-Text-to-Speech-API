import openai
import os
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import STTTranscription
from .serializers import STTTranscriptionSerializer
from rest_framework.permissions import IsAuthenticated


class STTConvertAPIView(generics.CreateAPIView):
    queryset = STTTranscription.objects.all()
    serializer_class = STTTranscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        audio = request.FILES.get("audio")
        language = request.data.get("language", "en")
        model = request.data.get("model", "whisper-1")

        if not audio:
            return Response({
                "code": "invalid_file",
                "message": "Audio file is required",
            }, status=status.HTTP_400_BAD_REQUEST)

        if not audio.name.lower().endswith((".mp3", ".wav", ".m4a")):
            return Response({
                "code": "invalid_file",
                "message": "Unsupported file format",
                "details": {
                    "supported_formats": ["mp3", "wav", "m4a"],
                    "provided_format": audio.name.split('.')[-1]
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        if audio.size > 25 * 1024 * 1024:
            return Response({
                "code": "file_too_large",
                "message": "Audio file exceeds maximum size limit of 25MB"
            }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        instance = STTTranscription.objects.create(
            user=request.user,
            audio_file=audio,
            language=language,
            model=model,
            status="pending"
        )

        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            audio.seek(0)
            result = openai.Audio.transcribe(
                model=model,
                file=audio,
                response_format="json",
                language=language
            )

            instance.text = result.get("text", "")
            instance.status = "completed"
            instance.file_size = audio.size
            instance.file_name = audio.name
            instance.duration = round(audio.size / 16000, 2)  # taxminiy hisob
            instance.save()
        except Exception as e:
            instance.status = "failed"
            instance.error = str(e)
            instance.save()
            return Response({
                "code": "processing_failed",
                "message": "STT processing failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class STTRetrieveAPIView(generics.RetrieveAPIView):
    queryset = STTTranscription.objects.all()
    serializer_class = STTTranscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class STTHistoryAPIView(generics.ListAPIView):
    serializer_class = STTTranscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return STTTranscription.objects.filter(user=self.request.user).order_by('-created_at')
