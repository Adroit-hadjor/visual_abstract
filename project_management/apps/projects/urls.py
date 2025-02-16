from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    project_index,
    project_list_partial,
    project_create,
    project_create_form,
    project_update,
    project_delete,
    project_comments_partial,
    project_comment_add,
project_detail_comments,
ProjectViewSet,
project_add_member
)

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')

#urlpatterns = router.urls
urlpatterns = [
    path('', project_index, name='home'),
    path('list/', project_list_partial, name='project_list_partial'),
    path('projects/details/<int:pk>/', project_detail_comments, name='project_detail_comments'),
    path('create/', project_create, name='project_create'),
    path('create/form/', project_create_form, name='project_create_form'),
    path('<int:pk>/update/', project_update, name='project_update'),
    path('<int:pk>/delete/', project_delete, name='project_delete'),
    # Comment endpoints
    path('<int:pk>/comments/', project_comments_partial, name='project_comments_partial'),
    path('<int:pk>/comment/add/', project_comment_add, name='project_comment_add'),
path('<int:pk>/add_member/', project_add_member, name='project_add_member'),

]