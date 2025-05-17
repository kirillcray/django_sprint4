from django.urls import path
from . import views
from .models import User

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="index"),
    path(
        "posts/<int:pk>/",
        views.PostDetailView.as_view(),
        name="post_detail"
    ),
    path(
        "category/<slug:category_slug>/",
        views.CategoryPostsView.as_view(),
        name="category_posts",
    ),
    path(
        "profile/edit_profile/",
        views.EditProfileView.as_view(),
        name="edit_profile",
    ),
    path(
        "profile/<slug:username>/",
        views.ProfileView.as_view(
            model=User, slug_field="username", slug_url_kwarg="username"
        ),
        name="profile",
    ),
    path("posts/create/", views.CreatePostView.as_view(), name="create_post"),
    path(
        "posts/<int:post_id>/comment/",
        views.AddCommentView.as_view(),
        name="add_comment",
    ),
    path(
        "posts/<int:post_id>/edit/",
        views.EditPostView.as_view(),
        name="edit_post"),
    path(
        "posts/<int:post_id>/edit_comment/<int:comment_id>/",
        views.EditCommentView.as_view(),
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/delete/",
        views.DeletePostView.as_view(),
        name="delete_post",
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:comment_id>/",
        views.DeleteCommentView.as_view(),
        name="delete_comment",
    ),
]
