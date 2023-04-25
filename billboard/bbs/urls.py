from django.urls import path
from .views import *
from django.views.decorators.cache import cache_page


urlpatterns = [
    #path('bbs_list/', index, name='index'),
    path('', index, name='home'),
    path('bbs/', index, name='index_list'),
    path('bbs_list/', PostList.as_view(), name='news_list'),
    path('my_posts/', MyPostList, name='mypostlist'),
    path('my_comments/', MyCommentList, name='mycomments'),
    path('bbs/<int:id>/', detail, name='post_detail_show'),
    path('bbs/search/', PostSearch.as_view()),
    path('bbs/create/', PostCreate.as_view(), name='post_create'),
    path('bbs/<int:pk>/edit/', PostDetailEdit.as_view(), name='post_edit'),
    path('bbs/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('bbs/<int:pk>/comment_create/', comment_create_view, name='comment_create'),
    path('subscriptions/', subscriptions, name='subscriptions'),
    path('bbs/<int:id1>/comment/<int:id2>/edit/', comment_edit_view, name='comment_edit'),
    path('bbs/<int:id1>/comment/<int:id2>/delete/', comment_delete_view, name='comment_delete'),
    path('category/<slug:slug>/', postbycategory, name='category'),
    #path('', IndexView.as_view()), # для экспериментов

]