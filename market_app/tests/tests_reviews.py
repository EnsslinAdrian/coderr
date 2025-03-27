from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from auth_app.models import Profile
from market_app.models import Review
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


class AccountTests(APITestCase):
    def setUp(self):
        self.reviewer_user = User.objects.create_user(username='Laureni', password='secret')
        self.business_user = User.objects.create_user(username='Marceli', password='secret')

        self.reviewer_profile = Profile.objects.create(user=self.reviewer_user, first_name='Marcel', last_name='Tester', type='private')
        self.business_profile = Profile.objects.create(user=self.business_user, first_name='Lauren', last_name='Testerin', type='business')

        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.reviewer_user,
            rating=5,
            description='Sehr gute Arbeit immer wieder gerne!',
        )
        
        self.customer_token = Token.objects.create(user=self.reviewer_user)
        self.business_token = Token.objects.create(user=self.business_user)

        self.customer_client = APIClient()
        self.customer_client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)

        self.business_client = APIClient()
        self.business_client.credentials(HTTP_AUTHORIZATION='Token ' + self.business_token.key)

    def test_create_review(self):
        url = reverse('reviews-list')
        review = {
            'business_user': self.business_user.id,
            'reviewer': self.reviewer_user.id,
            'rating': 5,
            'description': 'Sehr gute Arbeit immer wieder gerne!',
        }

        response = self.customer_client.post(url, review, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_reviews_single(self):
        url = reverse('reviews-details', kwargs={'pk': self.review.id})
        response = self.customer_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_review_single(self):
        url = reverse('reviews-details', kwargs={'pk': self.review.id})
        review = {
            'description': 'Sehr gute Arbeit immer wieder gerne! Freue mich auf weiter zusammenarbeit!',
        }

        response = self.customer_client.patch(url, review, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_review_single(self):
        url = reverse('reviews-details', kwargs={'pk': self.review.id})
        response = self.customer_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

