"""Tests for models"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from decimal import Decimal


class ModelTests(TestCase):
    """Tests models"""

    def test_create_user_with_email_successful(self):
        """Test a user with email is successful"""
        email = "test@gmail.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@Example.COM", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises an ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "sample123")

    def test_create_superuser(self):
        """Test creating a super user"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_admin)

    def test_create_superuser(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'test123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='The recipe Title',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description',
        )

        self.assertEqual(str(recipe), recipe.title)
