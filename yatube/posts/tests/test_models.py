from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.post = PostModelTest.post
        self.group = PostModelTest.group

    def test_models_have_correct_object_names_post(self):
        """Проверка длины __str__ post"""
        self.assertEqual(str(self.post), self.post.text[:15])

    def test_models_have_correct_object_names_group(self):
        """Проверка названия группы __str__ post"""
        self.assertEqual(str(self.group), self.group.title)

    def test_verbose_name(self):
        """Проверка verbose_name"""
        field_verboses = {'author': 'Автор',
                          'group': 'Группа'}
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text(self):
        """Проверка заполнения help_text"""
        field_help_texts = {'group': 'Здесь можно выбрать группу'}
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value)
