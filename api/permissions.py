import re

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            if request.user.is_superuser or request.user.role == 'app':
                return True


class IsCurrentUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        print('----------------asdasdasdasd-')
        print(request.user, obj)
        if request.user == obj:
            return True


# Manager


class IsManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous and request.user.role == 'manager':
            return True


class IsCurrentManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'manager' and request.user == obj.manager:
            return True


class ActionCurrentManager(IsCurrentUser):
    def has_permission(self, request, view):
        pk = view.kwargs.get('pk')

        if pk.isdigits():
            if f"managers/{request.user.pk}/workers" in request.path:
                if request.user.pk == int(pk):
                    return True

            # for worker's manager action
            elif "/test" in request.path:
                pass


# Worker


class IsWorker(BasePermission):
    pass
