from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:page_title>", views.entry_page, name="entry_page"),
    path("searching/", views.searching, name="searching"),
    path("new_page/", views.new_page, name='new_page'),
    path("edit/", views.edit, name="edit"),
    path("save_changes/", views.save_changes, name="save_changes"),
    path("random_page/", views.random_page, name="random_page"),
]
 