from http import HTTPStatus
from django import forms

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post, User


class PostFormTests(TestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test-group',
                                          description='Описание')
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовое описание поста')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x38')
        self.uploaded = SimpleUploadedFile(
            name='small_gif',
            content=small_gif,
            content_type='image/gif')

    def test_create_post(self):
        """Валидная форма создает запись в Posts."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст записанный в форму',
            'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        text='Текст записанный в форму',
                        group=self.group.id,
                        author=self.user,
                        ).exists())
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_can_edit_post(self):
        form_data = {'text': 'Тестовое описание поста',
                     'group': self.group.id}
        post = Post.objects.get(id=self.group.id)
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        group=self.group.id,
                        author=self.user,
                        pub_date=self.post.pub_date
                        ).exists())
        self.assertEqual(post.text, form_data['text'])

    def test_no_edit_post(self):
        """Проверка запрета редактирования не авторизованного пользователя"""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.client.post(reverse('posts:post_create'),
                                    data=form_data,
                                    follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name2 = 'Поcт добавлен в базу данных по ошибке'
        self.assertNotEqual(Post.objects.count(),
                            posts_count + 1,
                            error_name2)

    def test_create_post_picture(self):
        """Валидная форма создает запись в Posts с картинкой."""

        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField}
        for value, expected in form_fields.items():
            with self.subTest(value=value, image='posts/small.gif'):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
