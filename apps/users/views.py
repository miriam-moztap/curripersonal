from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from random import randint

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..companies.models import Company
from ..companies.serializers import CompanySerializer
from ..general.helpers.db_validators import find_user, find_cv_obj_user
from ..general.authentication_middleware import Authentication
from ..general.token_generator import account_activation_token
from .serializers import (
    AddressSerializer,
    UserListSerializer,
    UserSerializer,
    UserUpdatePasswordSerializer,
    ValidateDataUpdateUserJSON
)
from .models import User, Address
from .validates import validate_role_email

"""
Registra un usuario y lista usuarios
* Lista los usuarios, de acuerdo a quien los solicite:
  - Superadministador: todos
  - Administrador: empresas, padawans y externos
* Agregar la paginación: from y limit
"""


class CreateListUser(APIView):

    permission_classes = (AllowAny, )
    url = settings.URL_ACTIVATE
    app_name = settings.APP_NAME

    @swagger_auto_schema(
        operation_description='Lista las usuarios registrados. Se requiere el rol de administrador',
        security=[{'Token': []}],
        manual_parameters=[
            openapi.Parameter(
                name='page_size',
                description='Define el número de usuarios a listar por página',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                name='page_number',
                description='Define el número de página que se listará',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            '200': openapi.Response(
                description='',
                examples={
                    "application/json": {
                            "data": [
                                {
                                    "id": 4,
                                    "address": {
                                        "id": 50,
                                        "street": "Huatulco",
                                        "num_int": 4,
                                        "num_ext": 8,
                                        "suburb": "Huatulco xD",
                                        "town": "Oaxaca",
                                        "state": "Oaxaca",
                                        "country": "México",
                                        "zip_code": "70988"
                                    },
                                    "role": {
                                        "id": 3,
                                        "name": "Company",
                                        "description": "Rol de la empresa"
                                    },
                                    "about_me": "Esto es un about_me",
                                    "name": "Ángel",
                                    "paternal_surname": "García",
                                    "mothers_maiden_name": "García",
                                    "birthdate": "2000-10-19",
                                    "email": "chepeaicrag12@gmail.com",
                                    "phone": "9581248091",
                                    "image": "http://localhost:8000/media/default.jpg",
                                    "gender": "H",
                                    "subscribed": True,
                                    "status": "Postulado"
                                },
                                {
                                    "id": 6,
                                    "address": None,
                                    "role": {
                                        "id": 5,
                                        "name": "Extern",
                                        "description": "Rol de la extern"
                                    },
                                    "about_me": None,
                                    "name": None,
                                    "paternal_surname": None,
                                    "mothers_maiden_name": None,
                                    "birthdate": None,
                                    "email": "chepeaicrag12@gmai.com",
                                    "phone": None,
                                    "image": "http://localhost:8000/media/default.jpg",
                                    "gender": None,
                                    "subscribed": False,
                                    "status": "Buscando trabajo"
                                }
                            ],
                        "page_size": "2",
                        "page_number": 1,
                        "pages": 11,
                        "count": 22,
                        "next_page": True
                    }
                }
            ),
            '400': openapi.Response(
                description='',
                examples={
                    "application/json": {
                        "message": "Esa página no contiene resultados"
                    }
                }
            )
        }
    )
    def get(self, request):
        page_number = request.GET.get('page_number', 1)
        page_size = request.GET.get('page_size', 10)
        users = User.objects.all().filter(
            is_active=True, status_delete=False, is_superuser=False)
        paginator = Paginator(users, page_size)
        try:
            page = paginator.page(page_number)
        except Exception as e:
            print(e)
            return Response({'message': 'Esa página no contiene resultados'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserListSerializer(
            page, many=True, context={'request': request})
        return Response({'data': serializer.data, 'page_size': page_size, 'page_number': page_number, 'pages': paginator.num_pages, 'count': paginator.count, 'next_page': page.has_next()}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description='Solicita el código de acceso mediante un correo.',
        security=[{'Bearer': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            example={
                "email": "chepeaicrag12@gmail.com",
                "role": 3
            }
        ),
        responses={
            '200': openapi.Response(
                description='',
                examples={
                    "application/json": {
                            "id": 4,
                        "address": {
                            "id": 50,
                            "street": "Huatulco",
                            "num_int": 4,
                            "num_ext": 8,
                            "suburb": "Huatulco xD",
                            "town": "Oaxaca",
                            "state": "Oaxaca",
                            "country": "México",
                            "zip_code": "70988"
                        },
                        "role": {
                            "id": 3,
                            "name": "Company",
                            "description": "Rol de la empresa"
                        },
                        "about_me": "Esto es un about_me",
                        "name": "Ángel",
                        "paternal_surname": "García",
                        "mothers_maiden_name": "García",
                        "birthdate": "2000-10-19",
                        "email": "chepeaicrag12@gmail.com",
                        "phone": "9581248091",
                        "image": "/media/default.jpg",
                        "gender": "H",
                        "subscribed": True,
                        "status": "Postulado"
                    }
                }
            ),
            '400': openapi.Response(
                description='',
                examples={
                    "application/json": {
                        "message": "El email chepeaicrag12@gmail.com ya está registrado",
                        "message": "El rol es requerido",
                        "message": "El rol o email deben ser no nulos",
                        "message": "El rol es válido con el email",
                        "message": "Este usuario debe acceder de forma diferente",
                        "message": "Esta empresa no está registrada, no puede acceder",
                    }
                }
            )
        }
    )
    def post(self, request):
        data = request.data.copy()
        role = data.get('role', None)
        if role is None:
            return Response({'message': 'El rol es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if int(role) == 1:
            return Response({'message': 'No puede crear un usuario con este rol'}, status=status.HTTP_400_BAD_REQUEST)
        data['role'] = int(role)
        validate, message_validate = validate_role_email(
            data['email'], data['role'])
        if not validate:
            return Response({'message': message_validate}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=request.data['email'], role=1)
        if user.exists():
            return Response({'message': 'Este usuario debe acceder de forma diferente'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=request.data['email']).first()
        data['password'] = get_random_string(randint(6, 8)).strip()
        if not user:
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        data['password'] = account_activation_token.make_token(user)
        serializer = UserUpdatePasswordSerializer(instance=user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user.save()
        User.email_message(f'Acceso a la plataforma {self.app_name}',
                           self.url, user, data['password'], 'register.html')
        user = UserListSerializer(user, many=False)
        token = Token.objects.all().filter(
            user=user.data['id']).first()
        if token:
            token.delete()
        return Response(user.data, status=status.HTTP_200_OK)


"""
Update user logueado
* La primera vez debe registrar la dirección, las otras veces solo la actualiza.
* Se requiere de la información de la dirección, usuario y de una flag
* Cambiar el address_update por validar si el campo user.address es None
"""


class UpdateUser(Authentication, APIView):

    @swagger_auto_schema(
        operation_description='Edita un usuario logueado. Si el address_update es false, quiere decir que va a editar la dirección y esto indica que ya tiene una dirección registrada el usuario, de lo contrario, con address_update en false, indica que se creará la dirección para el usuario. Requiere el header de token',
        security=[{'Bearer': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                'address': openapi.Schema(type=openapi.TYPE_OBJECT),
                'update_user': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            },
            example={
                "user": {
                    "about_me": "Esto es un about_me",
                    "name": "Ángel",
                    "paternal_surname": "García",
                    "mothers_maiden_name": "García",
                    "birthdate": "2000-10-19",
                    "gender": "H",
                    "subscribed": True,
                    "phone": "9581248091"
                },
                "address": {
                    "state": "Oaxaca",
                    "country": "México"
                },
                "address_update": False
            }
        ),
        responses={
            '200': openapi.Response(
                description='',
                examples={
                    "application/json": {
                        "id": 4,
                        "address": {
                            "id": 50,
                            "street": "Huatulco",
                            "num_int": 4,
                            "num_ext": 8,
                            "suburb": "Huatulco xD",
                            "town": "Oaxaca",
                            "state": "Oaxaca",
                            "country": "México",
                            "zip_code": "70988"
                        },
                        "role": {
                            "id": 3,
                            "name": "Company",
                            "description": "Rol de la empresa"
                        },
                        "about_me": "Esto es un about_me",
                        "name": "Ángel",
                        "paternal_surname": "García",
                        "mothers_maiden_name": "García",
                        "birthdate": "2000-10-19",
                        "email": "chepeaicrag12@gmail.com",
                        "phone": "9581248091",
                        "image": "/media/default.jpg",
                        "gender": "H",
                        "subscribed": True,
                        "status": "Postulado"
                    }
                }
            ),
            '400': openapi.Response(
                description='',
                examples={
                    "application/json": {
                        "message": "No existe la dirección dada",
                    }
                }
            )
        }
    )
    def put(self, request):
        data = ValidateDataUpdateUserJSON(data=request.data)
        if not data.is_valid():
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)
        data = data.validated_data
        address_update = bool(data.get('address_update'))
        data_address = data.get('address')  # self.data_address
        user = User.objects.get(id=self.user.id)
        user_serializer = UserListSerializer(user, many=False)
        user_serializer = user_serializer.data
        if not address_update:
            serializer_address = AddressSerializer(data=data_address)
            if not serializer_address.is_valid():
                return Response({'message': serializer_address.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            address = Address.objects.all().filter(
                id=user.address.id).first()
            if not address:
                return Response({'message': f'No existe la dirección dada', "user": user_serializer}, status=status.HTTP_400_BAD_REQUEST)
            serializer_address = AddressSerializer(address, data_address)
            if not serializer_address.is_valid():
                return Response({'message': serializer_address.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer_address.save()
        address = serializer_address.data
        data_user = data.get('user')  # self.data_user
        data_user['address'] = address['id']
        serializer = UserSerializer(user, data=data_user, partial=True)
        if not serializer.is_valid():
            return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        user = UserListSerializer(User.objects.get(id=user.id))
        return Response(user.data, status=status.HTTP_200_OK)


# Administrador elimina usuarios
class ListUpdateDeleteUser(Authentication, APIView):

    @swagger_auto_schema(
        operation_description='Lista la información de un usuario especifico con el id dado',
        security=[{'Bearer': []}],
        responses={
            '200': openapi.Response(
                description='',
                examples={
                    "application/json": {
                        "id": 4,
                        "address": {
                            "id": 50,
                            "street": "Huatulco",
                            "num_int": 4,
                            "num_ext": 8,
                            "suburb": "Huatulco xD",
                            "town": "Oaxaca",
                            "state": "Oaxaca",
                            "country": "México",
                            "zip_code": "70988"
                        },
                        "role": {
                            "id": 3,
                            "name": "Company",
                            "description": "Rol de la empresa"
                        },
                        "about_me": "Esto es un about_me",
                        "name": "Ángel",
                        "paternal_surname": "García",
                        "mothers_maiden_name": "García",
                        "birthdate": "2000-10-19",
                        "email": "chepeaicrag12@gmail.com",
                        "phone": "9581248091",
                        "image": "/media/default.jpg",
                        "gender": "H",
                        "subscribed": True,
                        "status": "Postulado"
                    }
                }
            ),
            '400': openapi.Response(
                description='',
                examples={
                    'application/json': {
                        'message': 'Usuario no encontado'
                    },
                }
            )
        }
    )
    def get(self, request, id):
        user = find_user(id)
        if user is None:
            return Response({'message': 'Usuario no encontado'}, status=status.HTTP_400_BAD_REQUEST)
        user_serializer = UserListSerializer(user)
        user_data = user_serializer.data
        if user_data['role']['id'] == 3:
            try:
                company = Company.objects.get(coordinate=user)
                user_data['company'] = CompanySerializer(company).data
            except:
                user_data['company'] = {}
        return Response(user_data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        """Vista para editar los campos del perfil de usuario que sean visibles."""

        logged_user = self.user
        data = request.data.copy()
        if logged_user.role.id != 2:
            return Response(
                {'message': 'El usuario no tiene el rol para esta acción.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = find_user(id)
        if user is None:
            return Response(
                {'message': 'Usuario no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        hidden_fields = data.get('hidden_fields', None)
        if hidden_fields is None or len(hidden_fields) == 0:
            return Response({'message': 'Campo no válido'}, status=status.HTTP_400_BAD_REQUEST)
        for field in hidden_fields:
            if not field in user.hidden_fields:
                user.hidden_fields.append(field)
                user.save()
            else:
                user.hidden_fields.remove(field)
                user.save()
            response = {'hidden_fields': user.hidden_fields}
        return Response(response, status=status.HTTP_200_OK)

    # Validar que el usuariop sea de company, entonces borrar las compañias que tiene
    # Preguntar cómo hacer el borrado
    @swagger_auto_schema(
        operation_description='Elimina un usuario especifico con el id dado',
        security=[{'Bearer': []}],
        responses={
            '200': openapi.Response(
                description='',
                examples={
                    "application/json": {
                        'message': 'Usuario eliminado satisfactoriamente'
                    }
                }
            ),
            '400': openapi.Response(
                description='Posibles mensajes de error',
                examples={
                    'application/json': [
                        {'message': 'Usuario no encontado'},
                        {'message': 'No puede eliminar este usuario'}
                    ]
                }
            )
        }
    )
    def delete(self, request, id):
        user = find_user(id)
        if user is None:
            return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
        if user.role == 1:
            return Response({'message': 'No puede eliminar este usuario'}, status=status.HTTP_400_BAD_REQUEST)
        cv = find_cv_obj_user(user) # Busca a un cv de acuerdo al id de usuario, para eliminarlo también.
        cv.status_delete = True
        cv.save()
        user.status_delete = True
        user.save()
        address = Address.objects.filter(
            id=user.address.id, status_delete=False).first()
        address.status_delete = True
        address.save()
        return Response({'message': 'Usuario eliminado satisfactoriamente'}, status=status.HTTP_200_OK)
