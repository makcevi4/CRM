from django.contrib.auth.models import Group
from django.db.models import Q
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'telegram',
            'role'
        ]
        read_only_fields = ['id', 'role']

    def create(self, validated_data):
        validated_data['role'] = 'manager'

        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        group = Group.objects.get(name='Managers')
        user.groups.add(group)
        user.save()

        return user


class ManagerWorkersSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'telegram',
            'groups'
        ]


class WorkerSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'telegram',
            'role',
            'manager',
            'groups'
        ]
        read_only_fields = ['id', 'role']


class WorkerCreationSerializer(WorkerSerializer):
    type = serializers.CharField(max_length=50, write_only=True)
    manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'telegram',
            'role',
            'type',
            'manager'
        ]
        read_only_fields = ['id', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        usertype = validated_data.pop('type')

        try:
            group = Group.objects.get(name=usertype.capitalize())
        except Group.DoesNotExist:
            raise serializers.ValidationError({'detail': "Incorrect value Type"})

        validated_data['role'] = 'worker'

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        user.groups.add(group)
        user.save()

        return user


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = '__all__'


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = '__all__'
