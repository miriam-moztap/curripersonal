from pyexpat import model
from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from .models import Address, User, Role


class RoleSerializer(ModelSerializer):

    class Meta():
        model = Role
        fields = ['id', 'name', 'description']


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = ('user_permissions', )
        extra_kwargs = {
            'password': {'write_only': True},
            'token': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(
            email=validated_data['email'],
            role=validated_data['role'],
        )
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)
        if password is not None:
            instance.set_password(password)
        instance.about_me = validated_data.get('about_me', instance.about_me)
        instance.name = validated_data.get('name', instance.name)
        instance.paternal_surname = validated_data.get(
            'paternal_surname', instance.paternal_surname)
        instance.mothers_maiden_name = validated_data.get(
            'mothers_maiden_name', instance.mothers_maiden_name)
        instance.birthdate = validated_data.get(
            'birthdate', instance.birthdate)
        instance.phone = validated_data.get(
            'phone', instance.phone)
        instance.image = validated_data.get(
            'image', instance.image)
        instance.gender = validated_data.get(
            'gender', instance.gender)
        instance.subscribed = validated_data.get(
            'subscribed', instance.subscribed)
        if not instance.address:
            instance.address = validated_data.get(
                'address', instance.address)
        instance.save()
        return instance


class UserUpdatePasswordSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = ('user_permissions', )
        extra_kwargs = {
            'password': {'write_only': True},
            'token': {'write_only': True},
        }

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserTokenSerializer(ModelSerializer):

    role = RoleSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'image', 'role', 'name',
                  'paternal_surname', 'mothers_maiden_name']


class AddressSerializer(ModelSerializer):

    class Meta:
        model = Address
        exclude = ('status_delete', )


class UserListSerializer(ModelSerializer):

    address = AddressSerializer()
    role = RoleSerializer()

    class Meta:
        model = User
        exclude = ('is_staff', 'status_delete', 'is_active', 'last_login',
                   'is_superuser', 'password', 'token', 'user_permissions', 'groups', 'date_joined')


class ValidateDataUpdateUserJSON(serializers.Serializer):

    user = serializers.JSONField()
    address = AddressSerializer()
    address_update = serializers.BooleanField()
