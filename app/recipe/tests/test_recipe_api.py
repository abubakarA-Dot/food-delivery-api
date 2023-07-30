"""
Tests for Recipe API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPE_URLS = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **params):
    """" Create and return a sample recipe """
    defaults = {
        'title': 'Simple recipe title',
        'time_minutes': 22,
        'price': Decimal('10.11'),
        'description': 'Sample recipe description',
        'link': 'http://example.com/recipe.pdf'
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

class PublicRecipeTests(TestCase):
    """Test unauthenticated API requests"""
    
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test Auth is required when calling recipe API"""
        res = self.client.get(RECIPE_URLS)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="test123")
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPE_URLS)
        
        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""
        otherUser = create_user(email="other@example.com", password="test123")
        create_recipe(user=otherUser)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URLS)
        
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)
        
        url = detail_url(recipe.id)
        res = self.client.get(url)
        
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPE_URLS, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
        
        
    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            user = self.user,
            title='Sample Recipe Title',
            link=original_link,
        )
        payload = {
            'title':'New Sample Recipe Title',
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)


    def test_full_update(self):
        """Test full update of a recipe."""
        original_link = "https://example.com/new-recipe.pdf"
        recipe = create_recipe(
            user = self.user,
            title='Sample Recipe Title',
            link=original_link,
            description='Sample description',
        )
        payload = {
            'title':'New Sample Recipe Title',
            'link': original_link,
            'description': 'New updated description',
            'time_minutes':10,
            'price':Decimal('3.12'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
        
        # or next approach
        
        # self.assertEqual(recipe.title, payload['title'])
        # self.assertEqual(recipe.link, original_link)
        # self.assertEqual(recipe.description, payload['description'])
        # self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        # self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.user, self.user)


    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(
            email='user2@eample.com',
            password='test123'
        )
        recipe = create_recipe(user=self.user)
        payload = {
            'user':new_user.id,
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)


    def test_delete_recipe(self):
        """Test delete a recipe."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).first())


    def test_recipe_other_users_give_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(
            email='other@eample.com',
            password='test123',
        )
        recipe = create_recipe(user=new_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).first())
