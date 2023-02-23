from django import forms

from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {'group': 'Группа', 'text': 'Текст поста',
                  'image': 'Картинка'}
        help_texts = {'group': 'Выберите группу', 'text': 'Текст нового поста'}

        def clean_text(self):
            data = self.cleaned_data['text']
            if '' in data.lower():
                raise forms.ValidationError('Это поле не может быть пустым')
            return self.cleaned_data


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Добавьте Текст комментария',
        }
