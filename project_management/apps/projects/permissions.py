from rest_framework import permissions
from .models import ProjectMembership


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners to edit or delete the project.
    Editors can edit some fields, but not delete the project or manage roles.
    Readers can only view.
    """

    def has_object_permission(self, request, view, obj):
        # obj is a Project instance here
        if request.method in permissions.SAFE_METHODS:
            # GET, HEAD, OPTIONS are safe methods
            # We must ensure user has at least 'reader' role
            return ProjectMembership.objects.filter(
                user=request.user, project=obj
            ).exists()

        # For non-safe methods (POST, PUT, PATCH, DELETE)
        # Only owners can update or delete the project
        membership = ProjectMembership.objects.filter(
            user=request.user, project=obj
        ).first()

        if not membership:
            return False

        if membership.role == 'owner':
            return True

        # If membership.role == 'editor', they can edit some fields but cannot delete the project.
        # You can refine logic here. For now, let's say only owners can delete,
        # but editors can update via PUT/PATCH.
        if membership.role == 'editor' and request.method in ['PUT', 'PATCH']:
            return True

        return False


class CanCommentOnProject(permissions.BasePermission):
    """
    Owners and Editors can add comments; Readers can only view comments.
    """
    def has_object_permission(self, request, view, obj):
        # obj is a Project instance or maybe a Comment instance
        membership = ProjectMembership.objects.filter(
            user=request.user, project=obj.project if hasattr(obj, 'project') else obj
        ).first()
        if not membership:
            return False

        return membership.role in ['owner', 'editor']
