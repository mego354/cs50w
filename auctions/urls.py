from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("creating", views.creating, name="creating"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_name>", views.category, name="category"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("add/<int:listing_id>", views.add, name="add"),
    path("remove/<int:listing_id>", views.remove, name="remove"),
    path("sell/<int:listing_id>", views.sell, name="sell"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("favourite", views.favourite, name="favourite"),
]
