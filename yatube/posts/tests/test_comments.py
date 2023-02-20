from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User, Post, Group, Comment


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
        self.comment = Comment.objects.create(
            author=self.user,
            text='Текст комментария')

    def test_form_add_comments(self):
        """Форма создает запись в коммент"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}
                    ), data=form_data, follow=True)
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
