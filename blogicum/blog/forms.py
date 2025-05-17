from django import forms
from .models import Post, Category, Location, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования поста блога."""

    class Meta:
        model = Post
        exclude = ("author",)
        widgets = {
            "pub_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "text": forms.Textarea(attrs={"rows": 10}),
        }
        labels = {
            "title": "Заголовок",
            "text": "Текст",
            "pub_date": "Дата и время публикации",
            "author": "Автор публикации",
            "location": "Местоположение",
            "category": "Категория",
            "is_published": "Опубликовано",
            "image": "Фото",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location"].queryset = Location.objects.filter(
            is_published=True
        )
        self.fields["category"].queryset = Category.objects.filter(
            is_published=True
        )


class CommentForm(forms.ModelForm):
    """Форма для создания комментария к посту блога."""

    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "text": "Комментарий",
        }


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
