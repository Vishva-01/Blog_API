from django.urls import path
from .views import *

urlpatterns = [

    path('msg/',msg),

    path('search/', SearchAPI.as_view()),
    path('userlist/', UserListAPI.as_view()),

    path('register/',RegisterAPI.as_view()),
    path('login/',LoginAPI.as_view()),

    path("user/",UserListAPI.as_view()),

    path('blogs/',Blogs.as_view()),
    path('blog/',BlogAPI.as_view()),
    path('comment/',CommentAPI.as_view()),

    path('approve/<int:pk>',status_Approved),
    path('reject/<int:pk>',status_Rejected),

    path('tag',TagsListCreateAPI.as_view()),
    path('tag/<int:pk>',TagsRetrieveUpdateDestroyAPI.as_view()),

    path('test_token/',test_token),

]