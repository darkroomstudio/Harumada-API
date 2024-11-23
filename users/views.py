from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import logout
from .models import User
from .serializers import UserSerializer, UserUpdateSerializer
from django.db import connection

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update', 'me']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get', 'put', 'patch', 'delete'])
    def me(self, request):
        if request.method == 'DELETE':
            # Verify password
            password = request.data.get('password')
            if not password:
                return Response(
                    {"detail": "Password is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not request.user.check_password(password):
                return Response(
                    {"detail": "Incorrect password."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Store user for deletion
            user = request.user

            # Log out first
            logout(request)

            # Delete user
            user.delete()

            return Response(
                {"detail": "Your account has been successfully deleted."},
                status=status.HTTP_200_OK
            )

        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
            
        # Handle PUT and PATCH
        partial = request.method == 'PATCH'
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=partial,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)