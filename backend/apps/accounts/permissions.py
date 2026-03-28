"""Custom permissions for the accounts app."""

from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsLibrarianOrAdmin(BasePermission):
    """Allow access to librarians and administrators."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ("librarian", "admin")


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: the requesting user must be the object owner
    or an admin / librarian.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role in ("admin", "librarian"):
            return True
        # If the object has a `user` attribute, compare it
        if hasattr(obj, "user"):
            return obj.user == request.user
        # If the object IS a user, compare directly
        return obj == request.user


class IsMember(BasePermission):
    """Allow access only to regular library members."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "member"
        )


class IsOwnerOrLibrarian(BasePermission):
    """Allow access if the user owns the resource or is a librarian/admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.role in ("admin", "librarian"):
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "member"):
            return obj.member.user == request.user
        return False


class ReadOnly(BasePermission):
    """Allow read-only access (GET, HEAD, OPTIONS)."""

    def has_permission(self, request, view):
        return request.method in ("GET", "HEAD", "OPTIONS")
