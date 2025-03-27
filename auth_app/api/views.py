from rest_framework import generics
from .serializers import ProfileSerializer
from auth_app.models import Profile
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound, PermissionDenied


class ProfileView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class ProfileSingleView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        lookup_value = self.kwargs.get('pk') or self.kwargs.get('user')

        try:
            profile = Profile.objects.get(pk=lookup_value)
        except Profile.DoesNotExist:
            try:
                profile = Profile.objects.get(user__id=lookup_value)
            except Profile.DoesNotExist:
                raise NotFound("Das Benutzerprofil wurde nicht gefunden.")

        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            if self.request.user != profile.user:
                raise PermissionDenied("Authentifizierter Benutzer ist nicht der Eigentümer Profils.")

        return profile


class BusinessProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(type='business')

class CustomerProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(type='customer')


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                profile = Profile.objects.get(user=user)
                return Response({
                    "token": token.key,
                    "username": user.username,
                    "email": user.email,
                    "user_id": user.id
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)