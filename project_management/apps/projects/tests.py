from .models import Project, ProjectMembership
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


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
        """Owner can create a project and gets membership role = 'owner'."""
        response = self.client.post(
            reverse('project_create'),  # adjust to your create route
            data={
                'name': 'My Project',
                'description': 'Some description'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)  # or 201 if that’s how you return
        self.assertTrue(Project.objects.filter(name='My Project').exists())
        proj = Project.objects.get(name='My Project')
        # Check membership
        membership = ProjectMembership.objects.filter(user=self.owner, project=proj).first()
        self.assertIsNotNone(membership)
        self.assertEqual(membership.role, 'Owner')

    def test_add_member(self):
        """Owner can add a user as editor, etc."""
        # First create a project
        project = Project.objects.create(name='TestPro', description='Desc', owner=self.owner)
        ProjectMembership.objects.create(user=self.owner, project=project, role='Owner')

        # Now simulate an HTMX POST to add_member
        response = self.client.post(
            reverse('project_add_member', args=[project.pk]),
            data={
                'user_id': self.editor.id,
                'role': 'editor'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertIn(response.status_code, [200, 201])  # depends on your logic
        membership = ProjectMembership.objects.filter(user=self.editor, project=project).first()
        self.assertEqual(membership.role, 'editor')

    def test_project_update(self):
        """Owner (or editor) can update a project. Reader cannot."""
        # Create project & membership
        project = Project.objects.create(name='Proj1', description='Old desc', owner=self.owner)
        ProjectMembership.objects.create(user=self.owner, project=project, role='Owner')

        # Owner updates
        response = self.client.post(
            reverse('project_update', args=[project.pk]),
            data={'name': 'Proj1 updated', 'description': 'New desc'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertEqual(project.description, 'New desc')

        # Try as reader
        # Must log out and log in as reader
        self.client.logout()
        self.client.login(username='reader', password='readerpass')

        response = self.client.post(
            reverse('project_update', args=[project.pk]),
            data={'name': 'Proj1 hack', 'description': 'Reader cannot update?'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # Your code might return 403 or 404 if not permitted
        self.assertIn(response.status_code, [403, 404])

    def test_project_delete(self):
        """Owner can delete, others cannot."""
        project = Project.objects.create(name='ToDelete', owner=self.owner)
        ProjectMembership.objects.create(user=self.owner, project=project, role='Owner')

        # Owner deletes
        response = self.client.post(
            reverse('project_delete', args=[project.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(name='ToDelete').exists())

        # Re-create to test non-owner
        project2 = Project.objects.create(name='SecondOne', owner=self.owner)
        ProjectMembership.objects.create(user=self.owner, project=project2, role='Owner')
        ProjectMembership.objects.create(user=self.editor, project=project2, role='editor')

        # Editor tries to delete
        self.client.logout()
        self.client.login(username='editor', password='editorpass')
        response = self.client.post(
            reverse('project_delete', args=[project2.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # Expect 403 or 404
        self.assertIn(response.status_code, [403, 404])
        self.assertTrue(Project.objects.filter(name='SecondOne').exists())

