# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse
from django.db.models import Q
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from .models import Course,CourseResource,Video
from operation.models import UserFavorite,CourseComments,UserCourse
from utils.mixin_utils import LoginRequiredMixin

# Create your views here.

class CourseListView(View):
    def get(self,request):
        all_courses = Course.objects.all().order_by("-add_time")

        hot_courses = Course.objects.all().order_by("-click_nums")[:3]

        #课程搜索
        search_keywords = request.GET.get('keywords',"")
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(detail__icontains=search_keywords))

        #课程排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == 'student':
                all_courses = all_courses.order_by("-student")
            elif sort == 'hot':
                all_courses = all_courses.order_by("-click_nums")
        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 10, request=request)

        courses = p.page(page)

        return render(request,'course-list.html',{
            'all_courses':courses,
            'sort':sort,
            'hot_courses':hot_courses,
        })


class VideoPlayView(View):

    #视频播放
    def get(self,request,video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        course.student += 1
        course.save()
        #查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user= request.user,course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user,course=course)
            user_course.save()


        user_cousers = UserCourse.objects.filter(course = course)
        user_ids = [user_couser.user.id for user_couser in user_cousers]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #取出所有课程ID
        course_ids = [user_couser.course_id for user_couser in all_user_courses]
        #获取学过该用户学过其他的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)

        return render(request, 'course-play.html', {
            "course": course,
            "all_resources": all_resources,
            "relate_courses": relate_courses,
            "video": video
        })


class CourseDetailView(View):
    #课程详情
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))

        #增加课程点击数
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user,fav_id=course.id,fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user,fav_id=course.course_org.id,fav_type=2):
                has_fav_org = True

        tag =course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:3]
        else:
            relate_courses = []
        return render(request,'course-detail.html',{
            'course':course,
            'relate_courses':relate_courses,
            'has_fav_course':has_fav_course,
            'has_fav_org':has_fav_org,

        })


class CourseInfoView(LoginRequiredMixin, View):
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))
        course.student += 1
        course.save()
        #查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user= request.user,course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user,course=course)
            course.student += 1
            course.save()
            user_course.save()

        user_cousers = UserCourse.objects.filter(course = course)
        user_ids = [user_couser.user_id for user_couser in user_cousers]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #取出所有课程ID
        course_ids = [user_couser.course_id for user_couser in all_user_courses]
        #获取学过该用户学过其他的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-video.html', {
            'course': course,
            'all_resources':all_resources,
            'relate_courses':relate_courses,
        })


class CourseCommentView(LoginRequiredMixin, View):
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id))
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            course.student += 1
            course.save()
            user_course.save()

        user_cousers = UserCourse.objects.filter(course=course)
        user_ids = [user_couser.user_id for user_couser in user_cousers]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程ID
        course_ids = [user_couser.course_id for user_couser in all_user_courses]
        # 获取学过该用户学过其他的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course)
        return render(request, 'course-comment.html', {
            'course': course,
            'all_resources': all_resources,
            'all_comments':all_comments,
            'relate_courses': relate_courses,
        })


class AddCommentView(View):
    #用户添加课程评论
    def post(self, request):
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", "")
        if int(course_id) > 0 and comments:
            course_comments = CourseComments()
            # get只能取出一条数据，如果有多条抛出异常。没有数据也抛异常
            # filter取一个列表出来，queryset。没有数据返回空的queryset不会抛异常
            course = Course.objects.get(id=int(course_id))
            # 外键存入要存入对象
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"评论成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"评论失败"}', content_type='application/json')