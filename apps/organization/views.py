# _*_ encoding:utf-8 _*_
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse,JsonResponse
from django.db.models import Q


from .models import CourseOrg,CityDict,Teacher
from .forms import UserAskForm
from courses.models import Course
from operation.models import UserFavorite
from courses.models import Course
# Create your views here.


class OrgView(View):
    def get(self,request):
        #课程
        all_orgs = CourseOrg.objects.all()
        hot_orgs = all_orgs.order_by("click_nums")[:3]
        #城市
        all_citys = CityDict.objects.all()

        #机构搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        city_id = request.GET.get('city', "")
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        #类别筛选
        category = request.GET.get('ct',"")
        if category:
            all_orgs = all_orgs.filter(category=category)

        sort = request.GET.get('sort', "")
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by("-students")
            elif sort == 'courses':
                all_orgs = all_orgs.order_by("-course_nums")

        org_nums = all_orgs.count()
        #对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1


        p = Paginator(all_orgs,10 ,request=request)

        orgs = p.page(page)
        return render(request,"org-list.html",{
            "all_orgs":orgs,
            "all_citys":all_citys,
            "org_nums":org_nums,
            "city_id":city_id,
            "category":category,
            "hot_orgs":hot_orgs,
            "sort":sort,
        })


class UserAskView(View):
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        userask_form.save(commit=True)


class AddUserAskView(View):
    def post(self, request):
        userask_form = UserAskForm(request.POST)

        if userask_form.is_valid():
            # userask_form 的 save 方法有个参数 commit, 默认就是为 True,
            # 是直接将数据保存到数据库中, 如果 commit 为 False, 则这里只是
            # 将结果提交到数据库, 但并没有真正保存到数据库
            user_ask = userask_form.save(commit=True)

            # 这里是进行 ajax 操作, 所以不能用 render 来返回整个页面,
            # 用 render 返回页面是要刷新整个页面的, 而进行 ajax 异步操作,
            # 这里应该返回 json, 通过 JsonResponse 返回 json 字符串,
            # JsonResponse 是 HttpResponse 的子类
            return JsonResponse(data='{"status": "success"}', safe=False)
        else:
            # 注意: 这里有个坑, data 是要返回到前端的 json, 标准 json 是用的
            # 双引号, 所以这里一定要在 json 中用 双引号, 花括号外面用单引号
            return JsonResponse(data='{"status": "fail", "error_msg": "填写错误!"}', safe=False)



class OrgHomeView(View):
    def get(self,request,org_id):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]

        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=int(course_org.id)):
                has_fav = True

        return render(request,'org-detail-homepage.html',
                      {'all_courses': all_courses, 'all_teachers': all_teachers, 'course_org': course_org,
                       'current_page': current_page, 'has_fav': has_fav})

class OrgCourseView(View):
    def get(self,request,org_id):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_courses = course_org.course_set.all()
        has_fav = False
        # 必须是用户已登录我们才需要判断。
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request,'org-detail-course.html',{
            'all_courses':all_courses,
            'course_org':course_org,
            'current_page':current_page,
            'has_fav': has_fav,
        })

class OrgDescView(View):
    def get(self,request,org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        # 必须是用户已登录我们才需要判断。
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request,'org-detail-desc.html',{

            'course_org':course_org,
            'current_page':current_page,
            'has_fav': has_fav,
        })

class OrgTeacherView(View):
    def get(self,request,org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teachers = course_org.teacher_set.all()
        has_fav = False
        # 必须是用户已登录我们才需要判断。
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

                # return redener加上值


        return render(request,'org-detail-teachers.html',{
            'all_teachers':all_teachers,
            'course_org':course_org,
            'current_page':current_page,
            'has_fav':has_fav,
        })

class AddFavView(View):
    def post(self, request):
        # 表明你收藏的不管是课程，讲师，还是机构。他们的id
        # 默认值取0是因为空串转int报错
        fav_id = request.POST.get('fav_id', '0')
        # 取到你收藏的类别，从前台提交的ajax请求中取
        fav_type = request.POST.get('fav_type', '0')

        # 收藏与已收藏取消收藏
        # 判断用户是否登录:即使没登录会有一个匿名的user
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:
            # 如果记录已经存在， 则表示用户取消收藏
            exist_records.delete()
            if int(fav_type) == 1:
                course = Course.objects.get(id= int(fav_id))
                course.fav_nums -= 1
                course.save()
            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id =int(fav_id))
                course_org.fav_nums -= 1
                course_org.save()
            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id =int(fav_id))
                teacher.fav_nums -= 1
                teacher.save()
            return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            # 过滤掉未取到fav_id type的默认情况
            if int(fav_type) > 0 and int(fav_id) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()

                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    if course.fav_nums < 0:
                        course.fav_nums = 0
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    if course_org.fav_nums < 0:
                        course_org.fav_nums = 0
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    if teacher.fav_nums < 0:
                        teacher.fav_nums = 0
                    teacher.save()


                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')


class TeacherListView(View):
    def get(self,request):
        all_teachers = Teacher.objects.all()

        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_teachers =all_teachers.filter(Q(name__icontains=search_keywords) |
                                              Q(work_company__icontains=search_keywords)|
                                              Q(work_position__icontains=search_keywords))

        sort = request.GET.get('sort', "")
        if sort:
            if sort == 'hot':
                all_teachers = all_teachers.order_by("-click_nums")

        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]

        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_teachers, 10, request=request)

        teachers = p.page(page)

        return render(request,'teachers-list.html',{
            'all_teachers':teachers,
            'sorted_teacher':sorted_teacher,
            'sort':sort

        })


class TeacherDetailView(View):
    def get(self,request,teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_nums += 1
        teacher.save()
        all_courses = Course.objects.filter(teacher= teacher)

        has_teacher_faved = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user= request.user,fav_type= 3,fav_id=teacher.id):
                has_teacher_faved = True

        has_org_faved = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
                has_org_faved = True

        #讲师排行
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]
        return render(request, 'teacher-detail.html', {
            'teacher':teacher,
            'all_courses':all_courses,
            'sorted_teacher':sorted_teacher,
            'has_teacher_faved':has_teacher_faved,
            'has_org_faved':has_org_faved,
        })








