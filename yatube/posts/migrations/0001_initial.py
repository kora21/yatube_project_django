# Generated by Django 2.2.16 on 2023-03-02 13:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200,
                                           verbose_name='Название')),
                ('slug', models.SlugField(unique=True,
                                          verbose_name='Название группы')),
                ('description', models.TextField(
                    verbose_name='Описание группы')),
            ],
            options={
                'verbose_name_plural': 'Группы',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Введите текст поста',
                                          verbose_name='Текст поста')),
                ('pub_date', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Дата публикации')),
                ('image', models.ImageField(blank=True, upload_to='posts/',
                                            verbose_name='Картинка')),
                ('author', models.ForeignKey(on_delete=django.db.models.
                                             deletion.CASCADE,
                                             related_name='posts',
                                             to=settings.AUTH_USER_MODEL,
                                             verbose_name='Автор')),
                ('group', models.ForeignKey(
                    blank=True,
                    help_text='Здесь можно выбрать группу',
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='posts',
                    to='posts.Group',
                    verbose_name='Группа')),
            ],
            options={
                'verbose_name': 'Пост',
                'verbose_name_plural': 'Посты',
                'ordering': ('-pub_date',),
                'default_related_name': 'posts',
            },
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.
                                             deletion.CASCADE,
                                             related_name='following',
                                             to=settings.AUTH_USER_MODEL,
                                             verbose_name='Подписчик')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.
                                           CASCADE, related_name='follower',
                                           to=settings.AUTH_USER_MODEL,
                                           verbose_name='Автор')),
            ],
            options={
                'ordering': ['-author'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('text', models.TextField(
                    help_text='Добавьте Текст комментария',
                    verbose_name='Текст комментария')
                 ),
                ('created', models.DateTimeField(auto_now_add=True,
                                                 verbose_name='Дата создания')
                 ),
                ('author', models.ForeignKey(on_delete=django.db.models.
                                             deletion.CASCADE,
                                             related_name='comments',
                                             to=settings.AUTH_USER_MODEL,
                                             verbose_name='Автор')),
                ('post', models.ForeignKey(blank=True, null=True,
                                           on_delete=django.db.models.deletion.
                                           CASCADE, related_name='comments',
                                           to='posts.Post',
                                           verbose_name='Комментарии')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ('-created',),
            },
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'),
                                               name='unique_participants'),
        ),
    ]
