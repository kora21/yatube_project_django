from http import HTTPStatus

from django import forms
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post, User

from .constants import (
    GROUP_DESCRIPTION,
    GROUP_SLUG,
    GROUP_TITLE,
    POST_TEXT,
)

POSTS_PER_PAGE = 10


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовое описание поста')
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        Post.objects.bulk_create([
            Post(
                text=f'{POST_TEXT} {i}', author=self.user, group=self.group
            ) for i in range(POSTS_PER_PAGE + 1)
        ])

    def test_paginator(self):
        urls_expected_post_number = [
            ['/', Post.objects.all()[:POSTS_PER_PAGE]],
            [f'/group/{self.group.slug}/', self.group.posts.all()
                [:POSTS_PER_PAGE]],
            [f'/profile/{self.user.username}/', self.user.posts.all()
                [:POSTS_PER_PAGE]],
        ]
        for url, queryset in urls_expected_post_number:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                page_obj = response.context.get('page_obj')
                self.assertIsNotNone(page_obj)
                self.assertIsInstance(page_obj, Page)
                self.assertQuerysetEqual(
                    page_obj.object_list, queryset, transform=lambda x: x
                )


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
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
            content_type='image/gif'
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug':
                            f'{self.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            f'{self.user.username}'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            self.post.id}): 'posts/post_create.html'}
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def post_index_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        form_fields = {
            'title': forms.fields.CharField,
            'text': forms.fields.CharField,
            'slug': forms.fields.SlugField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_index_show_image_context(self):
        """При вводе поста с картинкой изображение передается в контекст"""
        response = self.authorized_client.get(reverse(
            'posts:index'))
        self.assertEqual(response.context.get('page_obj')[0].image,
                         Post.objects.all()[0].image)

    def test_page_profile_show_image_context(self):
        """При вводе поста с картинкой изображение передается в контекст"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(response.context.get('page_obj')[0].image,
                         Post.objects.all()[0].image)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
                                              'posts:group_list',
                                              kwargs={'slug': 'test-slug'}))
        group_text_0 = {response.context['group'].title: 'Тестовая группа',
                        response.context['group'].slug: 'test_group'}
        for value, expected in group_text_0.items():
            self.assertEqual(group_text_0[value], expected)

    def test_profile_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(response.context.get('user').username, 'auth')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post_text_0 = {response.context['post'].text: 'Тестовый пост',
                       response.context['post'].group: self.group,
                       response.context['post'].author: self.user.username,
                       response.context['post'].image: 'posts/small.gif'}
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)

    def post_create_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def post_edit_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit'))
        form_fields = {
            'title': forms.fields.CharField,
            'text': forms.fields.CharField,
            'slug': forms.fields.SlugField,
        }
        expected = list(Post.objects.filter(post_id=self.post_id))
        self.assertEqual(response.context['post'], expected)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group)
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, 'поста нет на главной')
        self.assertIn(post, group, 'поста нет в профиле')
        self.assertIn(post, profile, 'поста нет в группе')

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='Тестовый пост',
            author=self.user,
        )
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)
