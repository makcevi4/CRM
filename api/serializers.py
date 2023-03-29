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

    def validate_type(self, value):
        try:
            return Group.objects.get(name=value.capitalize())
        except Group.DoesNotExist:
            raise serializers.ValidationError("Incorrect value")

    def create(self, validated_data):
        password = validated_data.pop('password')
        usertype = validated_data.pop('type')

        validated_data['role'] = 'worker'

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        user.groups.add(usertype)
        user.save()

        return user


class WorkerPasswordUpdateSerializer(WorkerSerializer):
    class Meta:
        model = User
        fields = ['password']

    def validate_password(self, value):
        if self.instance.check_password(value):
            raise serializers.ValidationError("The specified password must not match the current one.")

        return value


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

    def validate_worker_conversion(self, value):
        request = self.context.get('request')

        if self.instance is not None and value == self.instance.worker_conversion:
            raise serializers.ValidationError("The specified worker must not match the current one.")

        if value.role != 'worker':
            raise serializers.ValidationError("The specified user isn't worker.")

        if value.groups.all()[0].name.lower() != 'conversion':
            raise serializers.ValidationError("The specified worker isn't conversion.")

        if request.user.role == 'manager' and value.manager != request.user:
            raise serializers.ValidationError("You can't manage another manager's workers.")

        return value

    def validate_worker_retention(self, value):
        request = self.context.get('request')

        if self.instance is not None and value == self.instance.worker_retention:
            raise serializers.ValidationError("The specified worker must not match the current one.")

        if value is not None:
            if value.role != 'worker':
                raise serializers.ValidationError("The specified user isn't worker.")

            if value.groups.all()[0].name.lower() != 'retention':
                raise serializers.ValidationError("The specified worker isn't retention.")

            if request.user.role == 'manager' and value.manager != request.user:
                raise serializers.ValidationError("You can't manage another manager's workers.")

        return value


class ClientCreateOrUpdateByWorkerSerializer(ClientSerializer):
    class Meta:
        model = Client
        exclude = ['worker_conversion', 'worker_retention']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['worker_conversion'] = request.user

        return super(ClientCreateOrUpdateByWorkerSerializer, self).create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class CommentStaffSerializer(CommentSerializer):
    class Meta:
        model = Comment
        exclude = ['staff']


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = '__all__'


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = '__all__'
