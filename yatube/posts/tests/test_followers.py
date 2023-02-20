from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User, Follow


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(username='user')
        cls.user_following = User.objects.create_user(username='user_1')
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Тестовый текст',
        )

    def setUp(self):
        self.following_client = Client()
        self.follower_client = Client()
        self.following_client.force_login(self.user_following)
        self.follower_client.force_login(self.user_follower)

    def test_authorized_user_follow_correctly(self):
        """Проверка подписки на автора авторизованный пользователь"""
        follower_count = Follow.objects.count()
        self.follower_client.get(reverse('posts:profile_follow', args={
            self.user_following.username}))
        self.assertEqual(Follow.objects.count(), follower_count + 1)

    def test_authorized_user_unfollow_correctly(self):
        """Проверка отписки от автора авторизованный пользователь"""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        follower_count = Follow.objects.count()
        self.follower_client.get(reverse('posts:profile_unfollow',
                                 args=(self.user_following.username,)))
        self.assertEqual(Follow.objects.count(), follower_count - 1)

    def test_post_follows_displays_correctly(self):
        """Проверка страница появляется в ленте тех, кто подписан"""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post, response.context.get('page_obj'))

    def test_post_unfollowers_displays_correctly(self):
        """Проверка страница не появляется в ленте тех, кто не подписан"""
        response = self.following_client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post, response.context.get('page_obj'))
