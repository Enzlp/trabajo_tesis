from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Author
from .serializers import AuthorSerializer


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        # Limitar a 50 registros para pruebas
        return Author.objects.all()[:50]