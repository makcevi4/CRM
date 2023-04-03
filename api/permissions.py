from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from .models import User, Client, Comment, Deposit, Withdraw


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            if request.user.is_superuser or request.user.role == 'app':
                return True


class IsCurrentUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_anonymous and request.user == obj:
            return True


# Manager


class IsManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous and request.user.role == 'manager':
            return True


class IsCurrentManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_anonymous:
            match type(obj).__name__.lower():
                case 'user':
                    if request.user.role == 'manager' and request.user == obj.manager:
                        return True

                case 'client':
                    if obj.worker_conversion and obj.worker_conversion.manager == request.user:
                        return True

                    elif obj.worker_retention and obj.worker_retention.manager == request.user:
                        return True

                case 'comment':
                    pk = view.kwargs.get('pk')

                    if f"comments/{pk}/" in request.path:
                        comment = get_object_or_404(Comment, pk=pk)

                        if comment.staff == request.user:
                            return True

                case 'deposit' | 'withdraw' as option:
                    pk, manager, model = view.kwargs.get('pk'), request.user, None

                    match option:
                        case 'deposit':
                            model = Deposit
                        case 'withdraw':
                            model = Withdraw

                    client = model.objects.get(pk=pk).client

                    if client.worker_conversion.manager == manager:
                        return True
                    elif client.worker_retention is not None and client.worker_retention.manager == manager:
                        return True


class ActionCurrentManager(IsCurrentUser):
    def has_permission(self, request, view):
        pk = view.kwargs.get('pk')

        if not request.user.is_anonymous and request.user.role == 'manager' and pk.isdigit():
            if f"managers/{request.user.pk}/" in request.path:
                if request.user.pk == int(pk):
                    return True

            elif f"workers/{pk}/" in request.path:
                actions = ['update_password', 'comments']

                if view.action in actions and get_object_or_404(User, pk=pk, manager=request.user.pk):
                    return True

            elif f"clients/{pk}/" in request.path:
                actions = ['comments', 'deposits', 'withdraws', 'workers']

                if view.action in actions:
                    client = get_object_or_404(Client, pk=pk)

                    try:
                        if client.worker_conversion.manager == request.user:
                            return True

                        elif client.worker_retention and client.worker_retention.manager == request.user:
                            return True

                    except AttributeError:
                        pass


# Worker


class IsWorker(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous and request.user.role == 'worker':
            return True


class IsCurrentWorker(BasePermission):
    def has_object_permission(self, request, view, obj):
        match type(obj).__name__.lower():
            case 'client':
                if obj.worker_conversion and obj.worker_conversion == request.user:
                    return True

                elif obj.worker_retention and obj.worker_retention == request.user:
                    return True

            case 'comment':
                pk = view.kwargs.get('pk')

                if f"comments/{pk}/" in request.path:
                    comment = get_object_or_404(Comment, pk=pk)

                    if comment.staff == request.user:
                        return True

            case 'deposit' | 'withdraw' as option:
                pk, worker, model = view.kwargs.get('pk'), request.user, None

                match option:
                    case 'deposit':
                        model = Deposit
                    case 'withdraw':
                        model = Withdraw

                client = model.objects.get(pk=pk).client

                if client.worker_conversion == worker or client.worker_retention == worker:
                    return True


class ActionCurrentWorker(IsCurrentUser):
    def has_permission(self, request, view):
        pk = view.kwargs.get('pk')

        if not request.user.is_anonymous and request.user.role == 'worker' and pk.isdigit():
            if f"workers/{request.user.pk}/" in request.path:
                actions = ['manager', 'clients', 'comments']

                if view.action in actions and request.user.pk == int(pk):
                    return True

            elif f"clients/{pk}/" in request.path:
                actions = ['comments', 'deposits', 'withdraws']

                if view.action in actions:
                    client = get_object_or_404(Client, pk=pk)

                    if client.worker_conversion == request.user or client.worker_retention == request.user:
                        return True

            elif f"comments/{pk}/" in request.path:
                comment = get_object_or_404(Comment, pk=pk)

                if comment.staff == request.user:
                    return True
