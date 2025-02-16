from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Project, ProjectMembership, Comment
from .serializers import (
    ProjectSerializer,
    ProjectMembershipSerializer,
    CommentSerializer
)
from .permissions import IsProjectOwnerOrReadOnly, CanCommentOnProject
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from .models import Project
from django.contrib.auth.models import User
from django.db.models import Q

class ProjectViewSet(viewsets.ModelViewSet):
    """
    Handles:
    - list (GET)
    - retrieve (GET)
    - create (POST)
    - update (PUT/PATCH)
    - destroy (DELETE)
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrReadOnly]
'''
    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        ProjectMembership.objects.create(
            user=self.request.user, project=project, role='owner'
        )

    def get_queryset(self):
        # Return only projects where the user is a member (any role)
        return Project.objects.filter(members__user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_member(self, request, pk=None):
        """
        Endpoint: /projects/{project_id}/add_member/
        Body: { "user_id": <int>, "role": "editor" }
        Only owners should be able to do this.
        """
        project = self.get_object()
        # Check if current user is owner
        membership = ProjectMembership.objects.filter(user=request.user, project=project, role='owner').first()
        if not membership:
            return Response({"detail": "Only owners can add members."},
                            status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        role = request.data.get('role')
        if not user_id or not role:
            return Response({"detail": "user_id and role are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        existing_member = ProjectMembership.objects.filter(user_id=user_id, project=project).first()
        if existing_member:
            return Response({"detail": "User is already a member of this project."},
                            status=status.HTTP_400_BAD_REQUEST)

        ProjectMembership.objects.create(user_id=user_id, project=project, role=role)
        return Response({"detail": "Member added successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        """
        Endpoint: /projects/{project_id}/comment/
        Body: { "text": "Your comment text" }
        Only owners or editors can comment.
        """
        project = self.get_object()
        text = request.data.get('text')
        if not text:
            return Response({"detail": "Comment text is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        membership = ProjectMembership.objects.filter(user=request.user, project=project).first()
        if not membership or membership.role not in ['owner', 'editor']:
            return Response({"detail": "You do not have permission to comment on this project."},
                            status=status.HTTP_403_FORBIDDEN)

        comment = Comment.objects.create(project=project, user=request.user, text=text)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
'''

#htmx views


@login_required
@ensure_csrf_cookie
def project_index(request):
    """
    Render the main page that includes:
      - A container for the list of projects
      - A container for the create form
    """
    #projects = Project.objects.filter(owner=request.user)
    projects = Project.objects.filter(
        Q(owner=request.user)|(
        Q(members__user=request.user) &
        Q(members__role__in=['owner', 'editor', 'reader']))
    ).distinct()

    print('projects',projects)
    print('owner',request.user)
    pms = ProjectMembership.objects.all()
    print('projects',pms)


    # Load the first project's details & comments initially
    first_project = projects.first() if projects.exists() else None
    if first_project:
        first_comments = first_project.comments.select_related('user').order_by('-created_at')
    else:
        first_comments = []

    return render(request, 'projects/index.html', {
        'projects': projects,
        'first_project': first_project,
        'first_comments': first_comments
    })

@login_required
def project_list_partial(request):
    """
    Returns the partial template with all of the user's projects.
    This is used by HTMX to update #project-list-container.
    """
    projects = Project.objects.filter(owner=request.user)
    return render(request, 'projects/partials/_project_list.html', {
        'projects': projects
    })

@login_required
@require_http_methods(["POST"])
def project_create(request):
    """
    Handle project creation via HTMX POST.
    On success, return the updated list of projects as a partial.
    On error, return the create form partial with errors.
    """
    name = request.POST.get('name')
    description = request.POST.get('description', '').strip()

    if not name:
        # Return the create form partial with an error message
        return render(request, 'projects/partials/_project_create_form.html', {
            'error': 'Project name is required.',
            'name': name,
            'description': description
        }, status=400)

    # Create the project
    Project.objects.create(
        name=name,
        description=description,
        owner=request.user
    )
    project = Project.objects.filter(name=name,owner=request.user).first()

    ProjectMembership.objects.create(user_id=request.user.id, project=project, role='owner')

    # Return the updated list partial
    projects = Project.objects.filter(owner=request.user)
    return render(request, 'projects/partials/_project_list.html', {
        'projects': projects
    })

@login_required
def project_create_form(request):
    return render(request, 'projects/partials/_project_create_form.html')



@login_required
@require_http_methods(["POST"])
def project_delete(request, pk):
    """
    Delete the specified project. Return updated project list partial.
    """
    project = Project.objects.filter(pk=pk, owner=request.user)
    if(project.count()==0):
        print('cannnnt')
        messages.info(request, 'You cannot delete this project.You do not have the right privilege')
        response = HttpResponse()
        response["HX-Redirect"] = request.META.get("HTTP_REFERER", "/projects/")  # Redirect back
        return response
    project.delete()

    response = HttpResponse()
    response["HX-Redirect"] = request.META.get("HTTP_REFERER", "/projects/")  # Redirect back
    return response

@login_required
@require_http_methods(["GET", "POST"])
def project_update(request, pk):

    """
    If GET: returns an edit form for the specified project as partial HTML.
    If POST: updates the project and returns the updated project list partial
             OR just the updated row partial.
    """


    membership = ProjectMembership.objects.all()
    '''#print('membership', membership)
    if  membership[0] or membership.role not in ['owner', 'editor']:
        return HttpResponseForbidden("You are not allowed to edit this project.")
   '''
    #project = Project.object.filter(pk=pk, members__role__in=['editor'])
    project = get_object_or_404(Project,members__user=request.user.id ,pk=pk, members__role__in=['owner','editor'])

    if request.method == 'GET':
        # Return partial with the edit form
        return render(request, 'projects/partials/_project_update_form.html', {
            'project': project
        })

    else:
        # POST: update the project
        name = request.POST.get('name')
        description = request.POST.get('description', '').strip()
        if not project:
            return HttpResponseForbidden("Can't edit a prooject you did not create")
        if not name:
            return render(request, 'apps/projects/partials/_project_update_form.html', {
                'project': project,
                'error': 'Project name is required.',
            }, status=400)

        project.name = name
        project.description = description
        project.save()

        response = HttpResponse()
        response["HX-Redirect"] = request.META.get("HTTP_REFERER", "/projects/")  # Redirect back
        return response

        # Return the refreshed project list or row partial
        comments = project.comments.all().order_by('-created_at')
        return render(request, 'projects/partials/_detail_comments_oob.html', {
            'project': project,
            'comments': comments,
        })




@login_required
@require_http_methods(["GET", "POST"])
def project_add_member(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "GET":
        # Return a partial that includes the form for adding a member
        # e.g., we might pass all users except current ones
        all_users = User.objects.exclude(id=request.user.id)
        return render(request, "projects/partials/_add_member_form.html", {
            "project": project,
            "all_users": all_users
        })

    # POST logic
    user_idx = request.POST.get("user_id")
    role = request.POST.get("role")

    if not user_idx or not role:
        return HttpResponseBadRequest("Please select both user and role.")

    # You can add checks, e.g. only owners can add members:
    membership = ProjectMembership.objects.filter(user=request.user, project=project, role='owner').first()

    if not membership:
        return HttpResponseForbidden("Only owners can add members.")

    if ProjectMembership.objects.filter(user_id=user_idx, project=project).exists():
        return HttpResponseBadRequest("User is already a member of this project.")




    ProjectMembership.objects.create(user_id=user_idx, project=project, role=role)
    response = HttpResponse()
    response["HX-Redirect"] = request.META.get("HTTP_REFERER", "/projects/")  # Redirect back
    return response

    # Return updated membership list or a success partial
    '''return render(request, "projects/partials/_member_list.html", {
        "project": project,
        "members": project.members.select_related('user')
    })'''


@login_required
def project_comments_partial(request, pk):
    """
    Returns a partial showing all comments for a given project.
    """
    project = get_object_or_404(Project, pk=pk)
    comments = project.comments.select_related('user').order_by('-created_at')
    return render(request, 'projects/partials/_comment_list.html', {
        'project': project,
        'comments': comments,
    })

@login_required
def project_detail_comments(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # You might load comments, membership checks, etc.
    comments = project.comments.select_related('user').order_by('-created_at')

    # We'll render a single template that has the two OOB divs
    return render(request, 'projects/partials/_detail_comments_oob.html', {
        'project': project,
        'comments': comments
    })

@login_required
@require_http_methods(["POST"])
def project_comment_add(request, pk):
    """
    Adds a new comment to the project and returns the updated comment list.
    """
    print('here in project_comment_add')

    project = get_object_or_404(Project, pk=pk)

    text = request.POST.get('text', '').strip()



    membership = ProjectMembership.objects.filter(user=request.user, project=project).first()
    '''print('here in project_comment_add', membership)
    if not membership or membership.role not in ['owner', 'editor']:
        return HttpResponseForbidden("You are not allowed to edit this project.")'''
    if not text:
        # Return some partial with an error or the same form
        # Here we can re-render the comment list with an error message
        comments = project.comments.select_related('user').order_by('-created_at')
        return render(request, 'projects/partials/_comment_list.html', {
            'project': project,
            'comments': comments,
            'error': 'Comment text cannot be empty.',
        }, status=400)

    Comment.objects.create(project=project, user=request.user, text=text)

    # Return the updated list partial
    comments = project.comments.select_related('user').order_by('-created_at')
    return render(request, 'projects/partials/_comment_list.html', {
        'project': project,
        'comments': comments
    })
