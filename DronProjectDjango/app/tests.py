from django.test import TestCase
from django.urls import reverse
from .models import User

class UserAuthTests(TestCase):
    def test_register(self):
        resp = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
        })
        self.assertRedirects(resp, reverse('login'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login(self):
        User.objects.create_user(username='foo', email='foo@example.com', password='pass')
        resp = self.client.post(reverse('login'), {
            'username': 'foo@example.com',
            'password': 'pass',
        })
        self.assertRedirects(resp, reverse('home'))
