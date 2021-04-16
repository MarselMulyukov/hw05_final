from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.index, name="index"),
    path("follow/", views.follow_index, name="follow_index"),
    path("group/<slug:slug>/", views.group_posts, name="group-detail"),
    path("new", views.new_post, name="new-post"),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/<int:post_id>/", views.post_view, name="post"),
    path("<str:username>/<int:post_id>/edit/",
         views.post_edit, name="post-edit"),
    path("<username>/<int:post_id>/comment",
         views.add_comment, name="add-comment"),
    path("<str:username>/follow/",
         views.profile_follow, name="profile_follow"),
    path("<str:username>/unfollow/",
         views.profile_unfollow, name="profile_unfollow"),
]
