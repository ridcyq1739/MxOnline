# -*- coding:utf-8 -*-
__author__ = 'kreg'
__date__ = '2018/7/8 19:11'

from django.conf.urls import url,include
from .views import CourseListView,CourseDetailView,CourseInfoView,CourseCommentView,AddCommentView,VideoPlayView

app_name = 'courses'
urlpatterns = [
    url(r'^list/$',CourseListView.as_view(),name='course_list'),
    url(r'^detail/(?P<course_id>\d+)/$',CourseDetailView.as_view(),name='course_detail'),
    url(r'^info/(?P<course_id>\d+)/$',CourseInfoView.as_view(),name='course_info'),
    url(r'^comment/(?P<course_id>\d+)/$',CourseCommentView.as_view(),name='course_comment'),
    #添加用户评论
    url(r'^add_comment/$',AddCommentView.as_view(),name='add_comment'),
    url(r'^video/(?P<video_id>\d+)/$', VideoPlayView.as_view(), name="video_play"),

]