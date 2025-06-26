from django.urls import path
from .views import (
    TTSConvertAPIView, TTSRetrieveAPIView, TTSHistoryAPIView, TTSAudioRetrieveAPIView
)

urlpatterns = [
    path('tts/convert/', TTSConvertAPIView.as_view()),
    path('tts/<uuid:pk>/', TTSRetrieveAPIView.as_view()),
    path('tts/<uuid:pk>/audio/', TTSAudioRetrieveAPIView.as_view()),
    path('tts/history/', TTSHistoryAPIView.as_view()),
]
