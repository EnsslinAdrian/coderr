from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from auth_app.models import Profile
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='lauren', password='secret')

        self.profile = Profile.objects.create(
            first_name= 'Bob',
            last_name= 'Tester',
            location= 'Berlin',
            tel= '+4915123456789',
            description= 'Testprofil für UnitTest',
            working_hours= '9-17',
            type= 'customer',
            user= self.user,
            )

        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_profile_single(self):
        url = reverse('profile-detail', kwargs={'user': self.profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_profile_single(self):
        url = reverse('profile-detail', kwargs={'user': self.profile.id})
        profile = {
            'first_name': 'Stefan',
            'last_name': 'Musterman',
        }
        response = self.client.patch(url, profile, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_profile_single(self):
        url = reverse('profile-detail', kwargs={'user': self.profile.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
