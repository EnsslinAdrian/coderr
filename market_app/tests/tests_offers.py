from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from auth_app.models import Profile
from market_app.models import Offer
from rest_framework.authtoken.models import Token


class OffersTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='lauren', password='secret')
        self.profile = Profile.objects.create(user=self.user, first_name='Lauren', last_name='Testerin', type='business')
        self.offer = Offer.objects.create(title= 'Onlineshop', description= 'Professioneller Onlineshop', user=self.user)
        
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_offers(self):
        url = reverse('offers-list')
        offer = {
            'title': 'Onlineshop',
            'description': 'Professioneller Onlineshop',
            'user': self.user.id,
        }
        response = self.client.post(url, offer, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_single_offer(self):
        url = reverse('offers-details', kwargs={'pk': self.offer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.offer.title)

    def test_patch_offers_single(self):
        url = reverse('offers-details', kwargs={'pk': self.offer.id})
        data = {
            'title': 'Webistes',
            'description': 'Professionelle Websites',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_offers_single(self):
        url = reverse('offers-details', kwargs={'pk': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

