from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Post


class PostAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123"
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword123"
        )

        self.post = Post.objects.create(
            title="Test Post",
            content="Test content",
            author=self.user
        )

    def test_get_posts(self):
        response = self.client.get("/api/posts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/posts/",
            {
                "title": "New Post",
                "content": "New content"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data["author"],
            self.user.id
        )

    def test_create_post_unauthenticated(self):
        response = self.client.post(
            "/api/posts/",
            {
                "title": "New Post",
                "content": "New content"
            },
            format="json"
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]
        )

    def test_non_owner_cannot_update(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f"/api/posts/{self.post.id}/",
            {
                "title": "Hacked title"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_owner_can_update(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/posts/{self.post.id}/",
            {
                "title": "Updated title"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_owner_can_delete(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f"/api/posts/{self.post.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )