from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect

from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    CreateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from .forms import PostForm, CommentForm, UserForm
from .models import Post, Category, Comment, User
from django.views.generic.list import MultipleObjectMixin


class PostsMixin:
    """Миксин для отображения списка постов блога."""

    model = Post
    paginate_by = 10


class PostListView(PostsMixin, ListView):
    """Отображает список постов блога."""

    template_name = "blog/index.html"

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        ).order_by("-pub_date")


class CategoryPostsView(PostsMixin, ListView):
    """Отображает список постов блога по категории."""

    template_name = "blog/category.html"

    def get_queryset(self):
        category_slug = self.kwargs["category_slug"]
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True,
        )
        return Post.objects.filter(
            category=category,
            is_published=True,
            pub_date__lte=timezone.now(),
        ).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category,
            slug=self.kwargs["category_slug"],
            is_published=True,
        )
        return context


class PostDetailView(DetailView):
    """Отображает детальную информацию о посте блога."""

    model = Post
    template_name = "blog/detail.html"

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        # Если пост снят с публикации или запланирован, доступен только автору
        if (
            not post.is_published
            or post.pub_date > timezone.now()
            or not post.category.is_published
        ) and self.request.user != post.author:
            from django.http import Http404

            raise Http404()
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context["comments"] = Comment.objects.filter(
            post=post
        ).order_by("created_at")
        # Форма только для авторизованных пользователей
        if self.request.user.is_authenticated:
            context["form"] = CommentForm()
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    """Создает новый пост блога."""

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile",
            kwargs={"username": self.request.user.username},
        )


class EditPostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирует пост блога (только автор)."""

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"pk": self.object.pk},
        )

    def handle_no_permission(self):
        # Редирект на страницу поста, если пользователь не автор
        return redirect("blog:post_detail", pk=self.get_object().pk)


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаляет пост блога (только автор)."""

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"
    success_url = reverse_lazy("blog:index")

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.object — это пост, который собираются удалить
        context["form"] = PostForm(instance=self.object)
        return context

    def handle_no_permission(self):
        # Редирект на страницу поста, если пользователь не автор
        return redirect("blog:post_detail", pk=self.get_object().pk)


class ProfileView(DetailView, MultipleObjectMixin):
    """Отображает профиль пользователя и список его публикаций."""

    model = User
    template_name = "blog/profile.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Если текущий пользователь просматривает свой профиль —
        # показываем все его посты
        is_own_profile = (
            self.request.user.is_authenticated
            and self.request.user == self.object
        )
        if is_own_profile:
            object_list = Post.objects.filter(
                author=self.object
            ).order_by("-pub_date")
        else:
            object_list = Post.objects.filter(
                author=self.object,
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True,
            ).order_by("-pub_date")
        context = super().get_context_data(object_list=object_list, **kwargs)
        context["profile"] = self.object
        context["user"] = self.request.user
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Редактирует профиль пользователя."""

    model = User
    form_class = UserForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile",
            kwargs={"username": self.request.user.username},
        )


class AddCommentView(LoginRequiredMixin, CreateView):
    """Добавляет комментарий к посту."""

    model = Comment
    form_class = CommentForm
    template_name = "blog/add_comment.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"pk": self.kwargs["post_id"]},
        )


class EditCommentView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирует комментарий (только автор)."""

    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"pk": self.kwargs["post_id"]},
        )

    def handle_no_permission(self):
        # Редирект на страницу поста, если пользователь не автор
        return redirect("blog:post_detail", pk=self.get_object().pk)


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаляет комментарий (только автор)."""

    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"pk": self.kwargs["post_id"]},
        )

    def handle_no_permission(self):
        # Редирект на страницу поста, если пользователь не автор
        return redirect("blog:post_detail", pk=self.get_object().pk)
