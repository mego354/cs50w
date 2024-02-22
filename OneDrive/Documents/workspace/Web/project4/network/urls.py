
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("update_post/", views.update_post, name="update_post"),
    path("like_post/", views.like_post, name="like_post"),
    path("profile/<int:user_id>", views.profile, name="profile")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
