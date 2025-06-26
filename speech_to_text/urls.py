from django.urls import path
from .views import STTConvertAPIView, STTRetrieveAPIView, STTHistoryAPIView

urlpatterns = [
    path("stt/convert", STTConvertAPIView.as_view()),
    path("stt/<uuid:pk>", STTRetrieveAPIView.as_view()),
    path("stt/history", STTHistoryAPIView.as_view()),
]
