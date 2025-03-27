from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from auth_app.models import Profile
from market_app.models import Order
from rest_framework.authtoken.models import Token


class OrdersTests(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(username='Laureni', password='secret')
        self.business_user = User.objects.create_user(username='Marceli', password='secret')

        self.customer_profile = Profile.objects.create(user=self.customer_user, first_name='Marcel', last_name='Tester', type='private')
        self.business_profile = Profile.objects.create(user=self.business_user, first_name='Lauren', last_name='Testerin', type='business')

        self.offer = Order.objects.create (
            customer_user = self.customer_user,
            business_user = self.business_user,
            title = 'Website',
            revisions = 2,
            delivery_time_in_days = 5,
            price= 20.00,
            features= ['Logo Design', 'Visitenkarten'],
            offer_type= 'basic',
            status= 'in_progress',
        )

        self.customer_token = Token.objects.create(user=self.customer_user)
        self.business_token = Token.objects.create(user=self.business_user)

        self.customer_client = APIClient()
        self.customer_client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)

        self.business_client = APIClient()
        self.business_client.credentials(HTTP_AUTHORIZATION='Token ' + self.business_token.key)

    def test_get_single_orders(self):
        url = reverse('orders-details', kwargs={'pk': self.offer.id})
        response = self.customer_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.offer.title)

    def test_patch_offers_orders(self):
        url = reverse('orders-details', kwargs={'pk': self.offer.id})
        data = {
            'revisions': 3,
            'delivery_time_in_days': 7,
        }
        response = self.customer_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_offers_order(self):
        url = reverse('orders-details', kwargs={'pk': self.offer.id})
        response = self.customer_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
