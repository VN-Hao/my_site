from django.urls import path
from . import views

urlpatterns = [
    path("", views.starting_page, name="starting-page"),
    path("posts", views.posts_page, name="posts-page"),
    path("chat", views.ChatView.as_view(), name="chat"),
    path("posts/<slug:slug>", views.post_detail_page, name="post-detail-page"),
    path(
        "posts/<slug:slug>/level-<int:level_number>",
        views.game_level_page,
        name="game-level-page",
    ),
    path("verify-flag", views.verify_flag, name="verify-flag")
]
