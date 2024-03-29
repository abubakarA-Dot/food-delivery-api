"""
Views for RECIPE API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for Manage recipe API"""
    serializer_class = serializers.RecipeDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()


    def get_queryset(self):
        """"Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')


    def get_serializer_class(self):
        """Return the serializer  class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Validate serializer and create a new recipe."""
        serializer.save(user=self.request.user)
