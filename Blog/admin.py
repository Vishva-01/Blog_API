from django.contrib import admin
from .models import *

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'about') 
    
admin.site.register(BlogModel,BlogAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display=('user','comment','blog')
    
admin.site.register(CommentModel,CommentAdmin)

admin.site.register(TagModel)

class MailAdmin(admin.ModelAdmin):
    list_display=('email',MailModel)
    
admin.site.register(MailModel,MailAdmin)