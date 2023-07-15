"""
Serializers for Recipe API
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe API"""
    
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'price', 'link']
        read_only_fields = ['id']