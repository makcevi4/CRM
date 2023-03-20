from rest_framework.permissions import BasePermission


class IsCurrentUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        result = Fa
        print()


class IsRightManager(BasePermission):
    def has_permission(self, request, view):
        pass


class IsRightWorker(BasePermission):
    def has_permission(self, request, view):
        pass