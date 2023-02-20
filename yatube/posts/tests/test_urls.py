from http import HTTPStatus

from django.test import TestCase, Client

from posts.models import Group, Post, User

from .constants import (
    GROUP_DESCRIPTION,
    GROUP_SLUG,
    GROUP_TITLE,
)


class PostURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION)
        self.post = Post.objects.create(
            group=self.group,
            author=self.user,
            text='Тестовый пост')

    def test_url_exists_for_guest_client(self):
        """Страница / доступна любому пользователю."""
        templates: tuple = ('/',
                            f'/group/{self.group.slug}/',
                            f'/profile/{self.user.username}/',
                            f'/posts/{self.post.id}/')
        for template in templates:
            response = self.client.get(template)
            error_name = f'Ошибка: нет доступа до страницы {template}'
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_urls_authorized_client(self):
        """Доступ авторизованного пользователя"""
        pages: tuple = ('/create/',
                        f'/posts/{self.post.id}/edit/')
        for page in pages:
            response = self.authorized_client.get(page)
            error_name = f'Ошибка: нет доступа до страницы {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_404(self):
        code_404_url_names = ['/unexisting_page/']
        for address in code_404_url_names:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
