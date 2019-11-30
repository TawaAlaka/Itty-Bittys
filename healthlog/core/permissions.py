from rest_framework.permissions import BasePermission


class IsAPIUser(BasePermission):
    """
    Allows access to only those with an info ID.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.info_id)


class IsUnauthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and not request.user.is_authenticated)
