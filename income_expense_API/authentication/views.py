from urllib import request
from django.conf import settings
from django.shortcuts import render
from rest_framework import generics, status, views, permissions
from yaml import serialize
from .serializer import RegisterSerializer, EmailVerificationSerializer, LoginSerializer
from .models import User
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from loguru import logger
import jwt
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from drf_spectacular import openapi

class RegisterView(generics.GenericAPIView):
    """
    Create a new user.

    This view allows users to register with their email and password.

    **Request**:

    - Method: `POST`
    - URL: `/api/register/`
    - Request Body:

      ```json
      {
        "email": "user@example.com",
        "username": "username",
        "password": "password"
      }
      ```

    **Response**:

    - Status Code: 201 Created
    - Body:

      ```json
      {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        "is_verified": false
      }
      ```

    **Error Response**:

    - Status Code: 400 Bad Request
    - Body:

      ```json
      {
        "error": "Invalid input data"
      }
      ```
    """
    serializer_class = RegisterSerializer
    
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data = user)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        user_data = serializer.data
        
        user = User.objects.get(email = user_data['email'])
        
        token = RefreshToken.for_user(user).access_token
        
        current_site = get_current_site(request).domain
        relative_link = reverse('email_verify')
        
        absurl = 'http://' + current_site + relative_link + "?token=" + str(token)
        email_body = f"Hello {user.username}, use the link below to verify your email \n"+ absurl
        
        data = {
            'email_subject': 'Verify your email',
            'email_body': email_body,
            'to_email': user.email
        }
        
        
        Util.send_email(data)
        
        return Response(user_data, status = status.HTTP_201_CREATED)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='token', location=OpenApiParameter.QUERY, description='The activation token received by the user.', type=OpenApiTypes.STR),
        ],
       
    )
    def get(self, request):
        """
        Verify user email.

        This view allows users to verify their email by providing a valid activation token.

        **Request**:

        - Method: `GET`
        - URL: `/api/verify-email/`
        - Query Parameters:
          - `token` (string, required): The activation token.

        **Response**:

        - Status Code: 200 OK
          - Body:

            ```json
            {
              "email": "Successfully activated"
            }
            ```

        - Status Code: 400 Bad Request
          - Body:

            ```json
            {
              "error": "Activation Expired"  
            }
            ```
        - Status Code: 400 Bad Request
            - Body:

                ```json
                {
                    "error": "Invalid Token"
                }
                ```
        """
        token = request.GET.get('token')
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id = payload['user_id'])
            
            if not user.is_verified:
                user.is_verified = True
                user.save()
            
            return Response(
                {'email': 'Successfully activated'}, status = status.HTTP_200_OK
                )
        
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {'email': 'Activation Link Expired'}, status.HTTP_400_BAD_REQUEST
            )
            
        except jwt.exceptions.DecodeError as identifier:
            return Response(
                {'error': 'Invalid Token'}, status = status.HTTP_400_BAD_REQUEST
            )
            

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        
        return Response(serializer.data,
                        status = status.HTTP_200_OK)
        