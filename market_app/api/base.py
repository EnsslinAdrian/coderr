from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

class CustomBaseView(GenericAPIView):
    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"detail": "Benutzer ist nicht authentifiziert."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().handle_exception(exc)
