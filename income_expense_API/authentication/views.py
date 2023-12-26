from urllib import request, response
from django.conf import settings
from django.shortcuts import render
from rest_framework import generics, status, views, permissions
from yaml import serialize
from .serializer import (
  RegisterSerializer, EmailVerificationSerializer, LoginSerializer, ResetPasswordEmailRequestSerializer,
  SetNewPasswordSerializer
  
  )

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
from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
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
    renderer_classes = (UserRenderer,)
    
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

class RequestPasswordResetEmail(generics.GenericAPIView):
  
  serializer_class = ResetPasswordEmailRequestSerializer

  def post(self, request):
      serializer = self.serializer_class(data = request.data)
      email = request.data['email']
      
      if User.objects.filter(email = email).exists():
            user = User.objects.get(email = email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request = request).domain
            relative_link = reverse('password-reset-confirm', kwargs = {'uidb64': uidb64, 'token': token})
            absurl = 'http://' + current_site + relative_link
            email_body = f"Hello, \nUse the link below to reset your password \n"+ absurl
            
            data = {
                'email_subject': 'Reset your password',
                'email_body': email_body,
                'to_email': user.email
            }
            
            
            Util.send_email(data)
            
      
      return Response({
          'success': 'We have sent you a link to reset your password'
        }, status = status.HTTP_200_OK )
      
      
class PasswordTokenCheckAPI(generics.GenericAPIView):
  def get(self, request, uidb64, token):
    try:
      id = smart_str(urlsafe_base64_decode(uidb64))
      user = User.objects.get(id = id)
      
      if not PasswordResetTokenGenerator().check_token(user, token):
        return Response({
          'error': 'Token is not valid, please request a new one'
        }, status = status.HTTP_401_UNAUTHORIZED)
      
      return Response({
        'success': True,
        'message': 'Credentials Valid',
        'uidb64': uidb64,
        'token': token
      }, status = status.HTTP_200_OK)
      
    except DjangoUnicodeDecodeError as identifier:
      return Response({
        'error': 'Token is not valid, please request a new one'
      }, status = status.HTTP_401_UNAUTHORIZED)
      
      
      
class SetNewPasswordAPIView(generics.GenericAPIView):
  serializer_class = SetNewPasswordSerializer
  
  def patch(self, request):
    serializer = self.serializer_class(data = request.data)
    serializer.is_valid(raise_exception = True)
    
    return Response({
      'success': True,
      'message': 'Password reset successful'
    }, status = status.HTTP_200_OK)