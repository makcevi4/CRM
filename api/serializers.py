from rest_framework import serializers
from .models import *


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'telegram'
        )


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'telegram',
            'manager'
        )


class ClientSerializer(serializers.ModelSerializer):
    worker = WorkerSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = '__all__'
        depth = 1


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
