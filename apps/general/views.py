# Django
from django.contrib.sessions.models import Session
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

# Rest Framework
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

# Utilities
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import send_email_validation
import threading

# Token
from .token_generator import account_activation_token

# Authentication
from ..general.authentication_middleware import Authentication

# Database validators and queries
from ..general.helpers.db_validators import find_cv_languages, find_cv_language

# Models
from API.companies.models import Company
from ..users.models import User
from ..general.models import CVLanguage

# Serializers
from API.companies.serializers import CompanyOnlySerialiazer
from ..users.serializers import UserTokenSerializer
from ..general.serializers import CVLanguageSerializer, CVLanguageListSerializer


class Login(ObtainAuthToken):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description='Acceso al sistema, para obtener un token de verificación y poder realizar diferentes actividades de acuerdo a tu rol.',
        security=[{'Token': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            example={
                "email": "chepeaicrag12@gmail.com",
                "password": "b5moky-3c82d0ceab180a9c66dc37852ee4afdf",
            }
        ),
        responses={
            '200': openapi.Response(
                description='',
                examples={
                    "application/json": [
                        {
                            "token": "6f034543b723e8c29cc62b8ef0e2a092f4e2e1a6",
                            "user": {
                                "id": 4,
                                "email": "chepeaicrag12@gmail.com",
                                "image": "/media/default.jpg",
                                "role": {
                                    "id": 3,
                                    "name": "Company",
                                    "description": "Rol de la empresa"
                                },
                                "name": "Ángel",
                                "paternal_surname": "García",
                                "mothers_maiden_name": "García"
                            },
                            "company": {
                                "id": 1,
                                "name": "Empresa Nueva",
                                "description": "Es una empresa de prueba",
                                "logo": "/media/default.jpg",
                                "email": "chepeaicrag12@gmail.com",
                                "status": "Registrada",
                                "coordinate": 4
                            }
                        }, {
                            "token": "6f034543b723e8c29cc62b8ef0e2a092f4e2e1a6",
                            "user": {
                                "id": 4,
                                "email": "chepeaicrag12@gmail.com",
                                "image": "/media/default.jpg",
                                "role": {
                                    "id": 3,
                                    "name": "Company",
                                    "description": "Rol de la empresa"
                                },
                                "name": "Ángel",
                                "paternal_surname": "García",
                                "mothers_maiden_name": "García"
                            },
                        }
                    ]
                }
            ),
            '400': openapi.Response(
                description='',
                examples={
                    "application/json": [
                        {"message": "El email es requerido"},
                        {"message": "El token de acceso es requerido"},
                        {"message": "El token de acceso no es el correcto o ha expirado, solicite uno nuevo"},
                        {"message": "Este usuario está restringido de la plataforma"},
                        {"message": "No hay usuario con email dado"},
                    ]
                }
            ),
        }
    )
    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        if email is None:
            return Response({'message': 'El email es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if password is None:
            return Response({'message': 'El token de acceso es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).exists()
        if user:
            user = User.objects.get(email=email)
            is_valid_token = account_activation_token.check_token(
                user, password)
            if not is_valid_token:
                return Response({'message': 'El token de acceso no es el correcto o ha expirado, solicite uno nuevo'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not user.status_delete:
                request.data.setdefault('username', email)
                serializer = self.serializer_class(
                    data=request.data, context={'request': request})
                if serializer.is_valid():
                    user = serializer.validated_data['user']
                    token, created = Token.objects.get_or_create(user=user)
                    user_serializer = UserTokenSerializer(user)
                    response = {'token': token.key,
                                'user': user_serializer.data, }
                    if user_serializer.data['role']['id'] == 3:
                        response['company'] = CompanyOnlySerialiazer(
                            Company.objects.get(coordinate=user)).data
                    if created:
                        user.last_login = timezone.now()
                        user.save()
                        response['last_login'] = user.last_login
                        return Response(response, status=status.HTTP_201_CREATED)
                    else:
                        all_sessions = Session.objects.filter(
                            expire_date__gte=datetime.now())
                        if all_sessions.exists():
                            for session in all_sessions:
                                session_data = session.get_decoded()
                                if user.id == int(session_data.get('_auth_user_id')):
                                    session.delete()
                        token.delete()
                        token = Token.objects.create(user=user)
                        user.last_login = timezone.now()
                        user.save()
                        response['token'] = token.key
                        response['last_login'] = user.last_login
                        return Response(response, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Este usuario está restringido de la plataforma'},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'No hay usuario con email dado'}, status=status.HTTP_400_BAD_REQUEST)


class SendFeedBack(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        titulo = request.data.get('title', None)
        if titulo is None:
            return Response({'message': 'El titulo es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        comentario = request.data.get('comment', None)
        if comentario is None:
            return Response({'message': 'El comentario es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        scheme = request.is_secure() and "https" or "http"
        url_logo = f'{scheme}://{request.get_host()}/static/logo_color.png'

        context_dict = {
            'titulo': titulo,
            'comentario': comentario,
            'app_name': settings.APP_NAME,
            'url_logo': url_logo
        }

        message = render_to_string('feedback.html', context_dict)

        thread = threading.Thread(target=send_email_validation, args=(
            'Feedback del sistema CVS', [settings.EMAIL_FEEDBACK], message))

        thread.start()
        return Response({'message': 'El feedback ha sido enviado satisfactoriamente'}, status=status.HTTP_200_OK)


class CVLanguageListCreateAPIView(Authentication, APIView):
    def get(self, request):
        user = self.user
        if user.role.id != 2:
            return Response({
                'message': 'El usuario no tiene el rol para esta acción.'
            }, status=status.HTTP_400_BAD_REQUEST)

        qs = find_cv_languages()
        if qs is None:
            return Response({
                'message': 'No hay lenguajes de CV registrados.'
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = CVLanguageListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = self.user
        data = request.data
        if user.role.id != 2:
            return Response({
                'message': 'El usuario no tiene el rol para esta acción.'
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = CVLanguageSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Idioma de CV registrado satisfactoriamente.'
        }, status=status.HTTP_200_OK)


class CVLanguageRetrieveUpdateDeleteAPIView(Authentication, APIView):
    def get(self, request, id):
        user = self.user
        if user.role.id != 2:
            return Response({
                'message': 'El usuario no tiene el rol para esta acción.'
            }, status=status.HTTP_400_BAD_REQUEST)

        obj = find_cv_language(id)
        if obj is None:
            return Response({
                'message': 'No existe el idioma.'
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = CVLanguageListSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        data = request.data
        user = self.user
        if user.role.id != 2:
            return Response({
                'message': 'El usuario no tiene el rol para esta acción.'
            }, status=status.HTTP_400_BAD_REQUEST)

        obj = find_cv_language(id)
        if obj is None:
            return Response({
                'message': 'No existe el idioma.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CVLanguageSerializer(obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Idioma actualizado.'
        }, status=status.HTTP_200_OK)

    def delete(self, request, id):
        user = self.user
        if user.role.id != 2:
            return Response({
                'message': 'El usuario no tiene el rol para esta acción.'
            }, status=status.HTTP_400_BAD_REQUEST)

        obj = find_cv_language(id)
        if obj is None:
            return Response({
                'message': 'No existe el idioma.'
            }, status=status.HTTP_400_BAD_REQUEST)

        obj.status_delete = True
        obj.save()
        return Response({
            'message': 'Idioma eliminado satisfactoriamente.'
        }, status=status.HTTP_200_OK)