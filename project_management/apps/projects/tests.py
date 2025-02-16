from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Project, ProjectMembership


class ProjectTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='owner', password='ownerpass'
        )
        self.editor = User.objects.create_user(
            username='editor', password='editorpass'
        )
        self.reader = User.objects.create_user(
            username='reader', password='readerpass'
        )

        # Log in as owner
        self.client.login(username='owner', password='ownerpass')

    def test_create_project(self):
        """Owner can create a project and gets membership role = 'owner' (lowercase)."""
        response = self.client.post(
            reverse('project_create'),
            data={
                'name': 'My Project',
                'description': 'Some description'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # Your view returns status=200 on success
        self.assertEqual(response.status_code, 200)

        # Check that the project exists
        self.assertTrue(Project.objects.filter(name='My Project').exists())
        proj = Project.objects.get(name='My Project')

        # Check membership
        membership = ProjectMembership.objects.filter(user=self.owner, project=proj).first()
        self.assertIsNotNone(membership)
        # The code sets role='owner'
        self.assertEqual(membership.role, 'owner')

    def test_add_member(self):
        """Owner can add a user as editor, etc."""
        # First create a project
        project = Project.objects.create(name='TestPro', description='Desc', owner=self.owner)
        ProjectMembership.objects.create(user=self.owner, project=project, role='owner')

        # Now simulate HTMX POST to add_member
        response = self.client.post(
            reverse('project_add_member', args=[project.pk]),
            data={
                'user_id': self.editor.id,
                'role': 'editor'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # Your code returns HttpResponse() => default 200 for success
        self.assertIn(response.status_code, [200])

        membership = ProjectMembership.objects.filter(user=self.editor, project=project).first()
        self.assertEqual(membership.role, 'editor')

    def test_project_update(self):
        """Owner (or editor) can update a project. Reader cannot."""
        # Create project & membership
        project = Project.objects.create(name='Proj1', description='Old desc', owner=self.owner)
        ProjectMembership.objects.create(user=self.owner, project=project, role='owner')

        # Owner updates
        response = self.client.post(
            reverse('project_update', args=[project.pk]),
            data={'name': 'Proj1 updated', 'description': 'New desc'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # The code returns 200 on success
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertEqual(project.description, 'New desc')

        # Try as reader
        self.client.logout()
        self.client.login(username='reader', password='readerpass')

        response = self.client.post(
            reverse('project_update', args=[project.pk]),
            data={'name': 'Proj1 hack', 'description': 'Reader cannot update?'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # If membership does not exist with role in ['owner','editor'], your code does get_object_or_404 => 404
        self.assertIn(response.status_code, [403, 404])  # or just 404 if that's how the code is set
        project.refresh_from_db()
        # Should remain 'New desc', since no update
        self.assertEqual(project.description, 'New desc')

    def test_project_delete(self):
        """Owner can delete, others cannot (but code returns 200 either way)."""
        project = Project.objects.create(name='ToDelete', owner=self.owner)
        ProjectMembership.objects.create(user=self.owner, project=project, role='owner')

        # Owner deletes
        response = self.client.post(
            reverse('project_delete', args=[project.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # The code returns 200 & updates partial if success
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(name='ToDelete').exists())

        # Re-create to test non-owner
        project2 = Project.objects.create(name='SecondOne', owner=self.owner)
        # Owner membership
        ProjectMembership.objects.create(user=self.owner, project=project2, role='owner')
        # Editor membership
        ProjectMembership.objects.create(user=self.editor, project=project2, role='editor')

        # Editor tries to delete
        self.client.logout()
        self.client.login(username='editor', password='editorpass')
        response = self.client.post(
            reverse('project_delete', args=[project2.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # Your code returns 200 with a message or redirect, not 403
        self.assertEqual(response.status_code, 200)
        # The project should still exist because editor can't actually remove it
        self.assertTrue(Project.objects.filter(name='SecondOne').exists())
