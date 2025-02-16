from rest_framework import serializers
from django.contrib.auth.models import User
from apps.accounts.serializers import UserSerializer
from .models import Project, ProjectMembership, Comment

class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user'
    )

    class Meta:
        model = ProjectMembership
        fields = ['id', 'user', 'user_id', 'role', 'project']
        read_only_fields = ['id', 'project']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'project', 'user', 'text', 'created_at']
        read_only_fields = ['id', 'project', 'user', 'created_at']

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = ProjectMembershipSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'members', 'comments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'members', 'comments', 'created_at', 'updated_at']
