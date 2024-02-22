from django.contrib import admin
from .models import User, Post
# Register your models here.

class AdminUser(admin.ModelAdmin):
    list_display = ("id", "username")
class AdminPost(admin.ModelAdmin):
    list_display = ("id" ,"user","date")


admin.site.register(User, AdminUser)
admin.site.register(Post, AdminPost)