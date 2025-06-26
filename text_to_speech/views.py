from rest_framework.views import APIView
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import openai
import os
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.conf import settings
from .models import TTSConversion
from .serializers import TTSConversionSerializer


class TTSAudioRetrieveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        tts = get_object_or_404(TTSConversion, pk=pk, user=request.user)

        if not tts.audio_file:
            return Response(
                {"code": "not_found", "message": "TTS conversion not found or audio not yet generated"},
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(tts.audio_file.open('rb'), content_type='audio/mpeg')




class TTSRetrieveAPIView(generics.RetrieveAPIView):
    queryset = TTSConversion.objects.all()
    serializer_class = TTSConversionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class TTSHistoryAPIView(generics.ListAPIView):
    serializer_class = TTSConversionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TTSConversion.objects.filter(user=self.request.user).order_by('-created_at')


class TTSConvertAPIView(generics.CreateAPIView):
    serializer_class = TTSConversionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        text = data.get("text")
        voice = data.get("voice", "nova")
        language = data.get("language", "en")
        speed = float(data.get("speed", 1.0))

        if not text:
            return Response({
                "code": "invalid_input",
                "message": "Invalid input data",
                "details": {"text": ["Text is required and cannot be empty"]}
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (0.25 <= speed <= 4.0):
            return Response({
                "code": "invalid_input",
                "message": "Invalid input data",
                "details": {"speed": ["Speed must be between 0.25 and 4.0"]}
            }, status=status.HTTP_400_BAD_REQUEST)

        tts = TTSConversion.objects.create(
            user=request.user,
            text=text,
            voice=voice,
            language=language,
            speed=speed,
            status="pending"
        )

        try:
            openai.api_key = settings.OPENAI_API_KEY
            response = openai.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            file_path = f"media/tts_audio/{tts.id}.mp3"
            with open(file_path, "wb") as f:
                f.write(response.content)

            file_size = os.path.getsize(file_path)
            duration = round(file_size / 16000, 2)  # taxminiy: 16kbps

            tts.audio_file.name = f"tts_audio/{tts.id}.mp3"
            tts.status = "completed"
            tts.file_size = file_size
            tts.duration = duration
            tts.save()

        except Exception as e:
            tts.status = "failed"
            tts.error = str(e)
            tts.save()
            return Response({
                "code": "processing_failed",
                "message": "TTS processing failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(tts, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
