# apps/projects/admin.py
from django.contrib import admin
from .models import Project, ProjectMembership, Comment

admin.site.register(Project)
admin.site.register(ProjectMembership)
admin.site.register(Comment)
from django.contrib import admin

# Register your models here.
