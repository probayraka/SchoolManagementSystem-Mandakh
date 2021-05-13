import json

import requests
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import datetime

from school_management_app.forms import AddStudentForm, EditStudentForm
from school_management_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, \
    FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport, \
    NotificationStudent, NotificationStaffs, News, TNews, TComment, SComment, AdminHOD, Parents, PNews ,PComment, FeedBackParents, NotificationParents


def admin_home(request):
    student_count1=Students.objects.all().count()
    staff_count=Staffs.objects.all().count()
    subject_count=Subjects.objects.all().count()
    course_count=Courses.objects.all().count()
    parent_count=Parents.objects.all().count()

    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)

    course_all=Courses.objects.all()
    course_name_list=[]
    subject_count_list=[]
    student_count_list_in_course=[]
    for course in course_all:
        subjects=Subjects.objects.filter(course_id=course.id).count()
        students=Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    subjects_all=Subjects.objects.all()
    subject_list=[]
    student_count_list_in_subject=[]
    for subject in subjects_all:
        course=Courses.objects.get(id=subject.course_id.id)
        student_count=Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    staffs=Staffs.objects.all()
    attendance_present_list_staff=[]
    attendance_absent_list_staff=[]
    staff_name_list=[]
    for staff in staffs:
        subject_ids=Subjects.objects.filter(staff_id=staff.admin.id)
        attendance=Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
        attendance_present_list_staff.append(attendance)
        attendance_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)

    students_all=Students.objects.all()
    attendance_present_list_student=[]
    attendance_absent_list_student=[]
    student_name_list=[]
    for student in students_all:
        attendance=AttendanceReport.objects.filter(student_id=student.id,status=True).count()
        absent=AttendanceReport.objects.filter(student_id=student.id,status=False).count()
        leaves=LeaveReportStudent.objects.filter(student_id=student.id,leave_status=1).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves+absent)
        student_name_list.append(student.admin.username)



    return render(request,"hod_template/home_content.html",{"student_count":student_count1,"staff_count":staff_count,"parent_count":parent_count,"subject_count":subject_count,"course_count":course_count,"course_name_list":course_name_list,"subject_count_list":subject_count_list,"student_count_list_in_course":student_count_list_in_course,"student_count_list_in_subject":student_count_list_in_subject,"subject_list":subject_list,"staff_name_list":staff_name_list,"attendance_present_list_staff":attendance_present_list_staff,"attendance_absent_list_staff":attendance_absent_list_staff,"student_name_list":student_name_list,"attendance_present_list_student":attendance_present_list_student,"attendance_absent_list_student":attendance_absent_list_student,"admin":admin})

def add_staff(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_staff_template.html",{"admin":admin})

def add_staff_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        address=request.POST.get("address")
        default_profile_pic="/media/default.png"
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=2)
            user.staffs.address=address
            if profile_pic_url!=None:
                user.staffs.profile_pic=profile_pic_url
            else:
                user.staffs.profile_pic=default_profile_pic
            user.save()
            messages.success(request,"Багш амжилттай нэмлээ")
            return HttpResponseRedirect(reverse("add_staff"))
        except:
            messages.error(request,"Багш нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("add_staff"))

def add_course(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_course_template.html",{"admin":admin})

def add_course_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        course=request.POST.get("course")
        try:
            course_model=Courses(course_name=course)
            course_model.save()
            messages.success(request,"Анги амжилттай нэмлээ")
            return HttpResponseRedirect(reverse("add_course"))
        except Exception as e:
            print(e)
            messages.error(request,"Анги нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("add_course"))

def add_student(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    form=AddStudentForm()
    return render(request,"hod_template/add_student_template.html",{"form":form,"admin":admin})

def add_student_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            address=form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            course_id=form.cleaned_data["course"]
            sex=form.cleaned_data["sex"]

            default_profile_pic="/media/default.png"
            if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None
            try:
                user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=3)
                user.students.address=address

                course_obj=Courses.objects.get(id=course_id)
                user.students.course_id=course_obj

                session_year=SessionYearModel.object.get(id=session_year_id)
                user.students.session_year_id=session_year
                
                user.students.gender=sex
                if profile_pic_url!=None:
                    user.students.profile_pic=profile_pic_url
                else:
                    user.students.profile_pic=default_profile_pic
                user.save()
                messages.success(request,"Сурагч амжилттай нэмлээ")
                return HttpResponseRedirect(reverse("add_student"))
            except:
                messages.error(request,"Сурагч нэмэхэд алдаа гарлаа")
                return HttpResponseRedirect(reverse("add_student"))
        else:
            form=AddStudentForm(request.POST)
            return render(request, "hod_template/add_student_template.html", {"form": form})


def add_subject(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    courses=Courses.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"hod_template/add_subject_template.html",{"staffs":staffs,"courses":courses,"admin":admin})

def add_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_name=request.POST.get("subject_name")
        course_id=request.POST.get("course")
        course=Courses.objects.get(id=course_id)
        staff_id=2
        staff=CustomUser.objects.get(id=staff_id)

        try:
            subject=Subjects(subject_name=subject_name,course_id=course,staff_id=staff)
            subject.save()
            messages.success(request,"Хичээл амжилттай нэмлээ")
            return HttpResponseRedirect(reverse("add_subject"))
        except:
            messages.error(request,"Хичээл нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("add_subject"))


def manage_staff(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    staffs=Staffs.objects.all()
    return render(request,"hod_template/manage_staff_template.html",{"staffs":staffs,"admin":admin})

def manage_student(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    students=Students.objects.all()
    return render(request,"hod_template/manage_student_template.html",{"students":students,"admin":admin})

def manage_course(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    courses=Courses.objects.all()
    return render(request,"hod_template/manage_course_template.html",{"courses":courses,"admin":admin})

def manage_subject(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    subjects=Subjects.objects.all()
    return render(request,"hod_template/manage_subject_template.html",{"subjects":subjects,"admin":admin})

def edit_staff(request,staff_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    staff=Staffs.objects.get(admin=staff_id)
    return render(request,"hod_template/edit_staff_template.html",{"staff":staff,"id":staff_id,"admin":admin})

def edit_staff_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id=request.POST.get("staff_id")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        username=request.POST.get("username")
        address=request.POST.get("address")
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            user=CustomUser.objects.get(id=staff_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()

            staff_model=Staffs.objects.get(admin=staff_id)
            staff_model.address=address
            if profile_pic_url!=None:
                staff_model.profile_pic=profile_pic_url
            staff_model.save()
            messages.success(request,"Багш амжилттай заслаа")
            return HttpResponseRedirect(reverse("manage_staff"))
        except:
            messages.error(request,"Багш засахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))

def delete_staff(request,staff_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            user=CustomUser.objects.get(id=staff_id)
            user.delete()
            messages.success(request,"Багш амжилттай устгалаа")
            return HttpResponseRedirect(reverse("manage_staff"))
        except:
            messages.error(request,"Багш устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_staff"))


def edit_student(request,student_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    request.session['student_id']=student_id
    student=Students.objects.get(admin=student_id)
    form=EditStudentForm()
    form.fields['email'].initial=student.admin.email
    form.fields['first_name'].initial=student.admin.first_name
    form.fields['last_name'].initial=student.admin.last_name
    form.fields['username'].initial=student.admin.username
    form.fields['address'].initial=student.address
    form.fields['course'].initial=student.course_id.id
    form.fields['sex'].initial=student.gender
    form.fields['session_year_id'].initial=student.session_year_id.id
    return render(request,"hod_template/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username,"admin":admin})

def edit_student_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student_id=request.session.get("student_id")
        if student_id==None:
            return HttpResponseRedirect(reverse("manage_student"))

        form=EditStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            session_year_id=form.cleaned_data["session_year_id"]
            course_id = form.cleaned_data["course"]
            sex = form.cleaned_data["sex"]

            if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None
            try:
                user=CustomUser.objects.get(id=student_id)
                user.first_name=first_name
                user.last_name=last_name
                user.username=username
                user.email=email
                user.save()

                student=Students.objects.get(admin=student_id)
                student.address=address
                session_year = SessionYearModel.object.get(id=session_year_id)
                student.session_year_id = session_year
                student.gender=sex
                course=Courses.objects.get(id=course_id)
                student.course_id=course
                if profile_pic_url!=None:
                    student.profile_pic=profile_pic_url
                student.save()
                del request.session['student_id']
                messages.success(request,"Сурагч амжилттай заслаа")
                return HttpResponseRedirect(reverse("manage_student"))
            except:
                messages.error(request,"Сурагч засахад алдаа гарлаа")
                return HttpResponseRedirect(reverse("edit_student",kwargs={"student_id":student_id}))
        else:
            form=EditStudentForm(request.POST)
            student=Students.objects.get(admin=student_id)
            return render(request,"hod_template/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username})

def delete_student(request,student_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            user=CustomUser.objects.get(id=student_id)
            user.delete()

            messages.success(request,"Сурагч амжилттай устгалаа")
            return HttpResponseRedirect(reverse("manage_student"))
        except:
            messages.error(request,"Сурагч устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_student"))

def edit_subject(request,subject_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    subject=Subjects.objects.get(id=subject_id)
    courses=Courses.objects.all()
    staffs=CustomUser.objects.filter(user_type=2)
    return render(request,"hod_template/edit_subject_template.html",{"subject":subject,"admin":admin,"staffs":staffs,"courses":courses,"id":subject_id})

def edit_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_id=request.POST.get("subject_id")
        subject_name=request.POST.get("subject_name")
        staff_id=request.POST.get("staff")
        course_id=request.POST.get("course")

        try:
            subject=Subjects.objects.get(id=subject_id)
            subject.subject_name=subject_name
            staff=CustomUser.objects.get(id=staff_id)
            subject.staff_id=staff
            course=Courses.objects.get(id=course_id)
            subject.course_id=course
            subject.save()

            messages.success(request,"Хичээл амжилттай заслаа")
            return HttpResponseRedirect(reverse("manage_subject"))
        except:
            messages.error(request,"Хичээл засахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))

def delete_subject(request,subject_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            subject=Subjects.objects.get(id=subject_id)
            subject.delete()
            messages.success(request,"Хичээл амжилттай устгалаа")
            return HttpResponseRedirect(reverse("manage_subject"))
        except:
            messages.error(request,"Хичээл устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_subject"))


def edit_course(request,course_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    course=Courses.objects.get(id=course_id)
    return render(request,"hod_template/edit_course_template.html",{"course":course,"admin":admin,"id":course_id})

def edit_course_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        course_id=request.POST.get("course_id")
        course_name=request.POST.get("course")
        try:
            course=Courses.objects.get(id=course_id)
            print(Courses.course_name)
            course.course_name=course_name
            course.save()
            messages.success(request,"Анги амжилттай заслаа")
            return HttpResponseRedirect(reverse("manage_course"))
        except:
            messages.error(request,"Анги засахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))

def delete_course(request,course_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            course=Courses.objects.get(id=course_id)
            course.delete()
            messages.success(request,"Анги амжилттай устгалаа")
            return HttpResponseRedirect(reverse("manage_course"))
        except:
            messages.error(request,"Анги устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_course"))


def manage_session(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    sessions=SessionYearModel.object.all()
    return render(request,"hod_template/manage_session.html",{"sessions":sessions,"admin":admin})

def add_session(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/manage_session_template.html",{"admin":admin})

def add_session_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")

        try:
            sessionyear=SessionYearModel(session_start_year=session_start_year,session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Амжилттай нэмлээ")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request, "Алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_session"))

def edit_session(request,session_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    sessions=SessionYearModel.object.all()
    return render(request,"hod_template/edit_session_template.html",{"sessions":sessions,"admin":admin})

def edit_session_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        session_id=request.POST.get("session_id")
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")

        try:
            sessionyear=SessionYearModel.object.get(id=session_id)
            sessionyear.session_start_year=session_start_year
            sessionyear.session_end_year=session_end_year
            sessionyear.save()

            messages.success(request, "Амжилттай заслаа")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request, "Засхад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_session"))

def delete_session(request,session_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            session=SessionYearModel.object.get(id=session_id)
            session.delete()
            messages.success(request,"Амжилттай устгалаа")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request,"Устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_session"))

def manage_news(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news=News.objects.all()
    return render(request,"hod_template/manage_news.html",{"news":news,"admin":admin})

def add_news(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_news_template.html",{"admin":admin})

def add_news_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name, pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=News(ntitle=ntitle,ntext=ntext)
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Мэдээ амжилттай нэмлээ")
            return HttpResponseRedirect(reverse("manage_news"))
        except:
            messages.error(request,"Мэдээ нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_news"))

def edit_news(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    if len(News.objects.filter(pk=news_id)) == 0:
        messages.error(request,"Мэдээ олдсонгүй")
        return HttpResponseRedirect(reverse("manage_news"))
    news=News.objects.get(id=news_id)
    return render(request,"hod_template/edit_news_template.html",{"news":news,"admin":admin})

def edit_news_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        news_id=request.POST.get("news_id")
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name,pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=News.objects.get(id=news_id)
            mv.ntitle=ntitle
            mv.ntext=ntext
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Мэдээ амжилттай заслаа")
            return HttpResponseRedirect(reverse("manage_news"))
        except:
            messages.error(request,"Мэдээ засахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_news"))

def delete_news(request,news_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=News.objects.get(id=news_id)
            mv.delete()
            messages.success(request,"Мэдээ амжилттай устгалаа")
            return HttpResponseRedirect(reverse("manage_news"))
        except:
            messages.error(request,"Мэдээ устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_news"))

def view_news(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news = News.objects.get(id=news_id)
    comment=SComment.objects.filter(News=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request,"hod_template/view_news.html",{"news":news,"comment":comment,"admin":admin,"comment_count":comments_count,"staff":staff})
    

def manage_tnews(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news = TNews.objects.all()
    return render(request,"hod_template/manage_tnews.html",{"news":news,"admin":admin})

def add_tnews(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_tnews_template.html",{"admin":admin})

def add_tnews_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name, pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=TNews(ntitle=ntitle,ntext=ntext)
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Мэдээ амжилттай нэмлээ")
            return HttpResponseRedirect(reverse("manage_tnews"))
        except:
            messages.error(request,"Мэдээ нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_tnews"))

def edit_tnews(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    if len(TNews.objects.filter(pk=news_id)) == 0:
        messages.error(request,"Мэдээ олдсонгүй")
        return HttpResponseRedirect(reverse("manage_tnews"))
    news=TNews.objects.get(id=news_id)
    return render(request,"hod_template/edit_tnews_template.html",{"news":news,"admin":admin})

def edit_tnews_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        news_id=request.POST.get("news_id")
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name,pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=TNews.objects.get(id=news_id)
            mv.ntitle=ntitle
            mv.ntext=ntext
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Мэдээ амжилттай заслаа")
            return HttpResponseRedirect(reverse("manage_tnews"))
        except:
            messages.error(request,"Мэдээ засахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_tnews"))

def delete_tnews(request,news_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=TNews.objects.get(id=news_id)
            mv.delete()
            messages.success(request,"Мэдээ амжилттай устгалаа")
            return HttpResponseRedirect(reverse("manage_tnews"))
        except:
            messages.error(request,"Мэдээ устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_tnews"))

def view_tnews(request, news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news=TNews.objects.get(id=news_id)
    comment=TComment.objects.filter(TNews=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request,"hod_template/view_tnews.html",{"news":news,"admin":admin,"comment":comment,"comment_count":comments_count,"staff":staff})

# POST TEACHER COMMENT
def view_staff_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_tnews"))
    else:
        TNews = request.POST.get("TNews_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = TComment.objects.get(id=reply_id)
        try:
            Tcomment=TComment(TNews_id=TNews, staff_id=staff, body=body, count=a, reply=comment_qs)
            Tcomment.save()
            messages.success(request, "Сэтгэгдэл нэмэгдлээ!")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":TNews}))
        except:
            messages.error(request, "Сэтгэгдэл нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":TNews}))
# EDIT TEACHER COMMENT
def view_staff_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("manage_tnews"))
    else:
        comment_id = request.POST.get("comment_id")
        TNews = request.POST.get("TNews_id")
        body = request.POST.get("body")
        try:
            comment = TComment.objects.get(id=comment_id)
            comment.TNews_id=TNews
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Сэтгэгдэл засагдлаа!")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":TNews}))
        except:
            messages.error(request, "Сэтгэгдэл засахад алдаа гарлаа ")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":TNews}))

def delete_tcomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=TComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Сэтгэгдэл амжилттай устгалаа")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Сэтгэгдэл устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_tnews",kwargs={"news_id":news_id}))

# POST STUDENT COMMENT
def view_student_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_news"))
    else:
        SNews = request.POST.get("News_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = SComment.objects.get(id=reply_id)
        try:
            Scomment=SComment(News_id=SNews, staff_id=staff, body=body, count=a, reply=comment_qs)
            Scomment.save()
            messages.success(request, "Сэтгэгдэл нэмэгдлээ!")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":SNews}))
        except:
            messages.error(request, "Сэтгэгдэл нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":SNews}))

# EDIT STUDENT COMMENT
def view_student_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("manage_news"))
    else:
        comment_id = request.POST.get("comment_id")
        SNews = request.POST.get("News_id")
        body = request.POST.get("body")
        try:
            comment = SComment.objects.get(id=comment_id)
            comment.News_id=SNews
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Сэтгэгдэл засагдлаа!")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":SNews}))
        except:
            messages.error(request, "Сэтгэгдэл засахад алдаа гарлаа ")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":SNews}))

# DELETE STUDENT COMMENT
def delete_scomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=SComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Сэтгэгдэл амжилттай устгалаа")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Сэтгэгдэл устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_news",kwargs={"news_id":news_id}))

@csrf_exempt
def check_email_exist(request):
    email=request.POST.get("email")
    user_obj=CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def staff_feedback_message(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    feedbacks=FeedBackStaffs.objects.all()
    return render(request,"hod_template/staff_feedback_template.html",{"feedbacks":feedbacks,"admin":admin})

def student_feedback_message(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    feedbacks=FeedBackStudent.objects.all()
    return render(request,"hod_template/student_feedback_template.html",{"feedbacks":feedbacks,"admin":admin})

def parent_feedback_message(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    feedbacks=FeedBackParents.objects.all()
    return render(request,"hod_template/parent_feedback_template.html",{"feedbacks":feedbacks,"admin":admin})

@csrf_exempt
def student_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def staff_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def parent_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackParents.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def staff_leave_view(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    leaves=LeaveReportStaff.objects.all()
    return render(request,"hod_template/staff_leave_view.html",{"leaves":leaves,"admin":admin})

def student_leave_view(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    leaves=LeaveReportStudent.objects.all()
    return render(request,"hod_template/student_leave_view.html",{"leaves":leaves,"admin":admin})

def student_approve_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))

def student_disapprove_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def staff_approve_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

def staff_disapprove_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

def admin_view_attendance(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    subjects=Subjects.objects.all()
    session_year_id=SessionYearModel.object.all()
    return render(request,"hod_template/admin_view_attendance.html",{"subjects":subjects,"admin":admin,"session_year_id":session_year_id})

@csrf_exempt
def admin_get_attendance_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Subjects.objects.get(id=subject)
    session_year_obj=SessionYearModel.object.get(id=session_year_id)
    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/admin_profile.html",{"user":user,"admin":admin})

def admin_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            admin=AdminHOD.objects.get(admin=customuser)
            if profile_pic_url!=None:
                admin.profile_pic=profile_pic_url
            admin.save()
            customuser.first_name=first_name
            customuser.last_name=last_name
            # if password!=None and password!="":
            #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Мэдээлэл шинэчлэгдлээ")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Мэдээлэл шинэчлэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("admin_profile"))

def admin_send_notification_student(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    students=Students.objects.all()
    return render(request,"hod_template/student_notification.html",{"students":students,"admin":admin})

def admin_send_notification_staff(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    staffs=Staffs.objects.all()
    return render(request,"hod_template/staff_notification.html",{"staffs":staffs,"admin":admin})

def admin_send_notification_parent(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    parent=Parents.objects.all()
    return render(request,"hod_template/parent_notification.html",{"parent":parent,"admin":admin})

def add_parent(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    students=Students.objects.all()
    return render(request,"hod_template/add_parent_template.html",{"students":students,"admin":admin})

def add_parent_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        student=request.POST.get("student")
        default_profile_pic="/media/default.png"
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=4)
            if profile_pic_url!=None:
                user.parents.profile_pic=profile_pic_url
            else:
                user.parents.profile_pic=default_profile_pic
            student_obj=Students.objects.get(id=student)
            user.parents.student_id=student_obj
            user.save()
            messages.success(request,"Эцэг эх амжилттай нэмлээ")
            return HttpResponseRedirect(reverse("add_parent"))
        except:
            messages.error(request,"Эцэг нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("add_parent"))

def edit_parent(request,parent_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    parent=Parents.objects.get(admin=parent_id)
    students=Students.objects.all()
    return render(request,"hod_template/edit_parent_template.html",{"parent":parent,"admin":admin,"students":students})


def edit_parent_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        parent_id=request.POST.get("parent_id")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        student=request.POST.get("student")
        if request.FILES.get('profile_pic',False):
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None
        try:
            user=CustomUser.objects.get(id=parent_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()
            parent=Parents.objects.get(admin=parent_id)
            if profile_pic_url!=None:
                parent.profile_pic=profile_pic_url
            student_obj=Students.objects.get(id=student)
            parent.student_id=student_obj
            parent.save()
            messages.success(request,"Эцэг эх амжилттай заслаа")
            return HttpResponseRedirect(reverse("manage_parent"))
        except:
            messages.error(request,"Эцэг эх засахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("edit_parent",kwargs={"parent_id":parent_id}))

def delete_parent(request,parent_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            user=CustomUser.objects.get(id=parent_id)
            user.delete()
            messages.success(request,"Эцэг эх амжилттай устгалаа")
            return HttpResponseRedirect(reverse("manage_parent"))
        except:
            messages.error(request,"Эцэг эх устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_parent"))

def manage_parent(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    parents=Parents.objects.all()
    return render(request,"hod_template/manage_parent_template.html",{"parents":parents,"admin":admin})

def manage_pnews(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news=PNews.objects.all()
    return render(request,"hod_template/manage_pnews.html",{"news":news,"admin":admin})

def add_pnews(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/add_pnews_template.html",{"admin":admin})

def add_pnews_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name, pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=PNews(ntitle=ntitle,ntext=ntext)
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Мэдээ амжилттай нэмлээ")
            return HttpResponseRedirect(reverse("manage_pnews"))
        except:
            messages.error(request,"Мэдээ нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_pnews"))

def view_pnews(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    news=PNews.objects.get(id=news_id)
    comment=PComment.objects.filter(PNews=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request,"hod_template/view_pnews.html",{"news":news,"comment":comment,"admin":admin,"comment_count":comments_count,"staff":staff})

def edit_pnews(request,news_id):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    if len(PNews.objects.filter(pk=news_id)) == 0:
        messages.error(request,"Мэдээ олдсонгүй")
        return HttpResponseRedirect(reverse("manage_tnews"))
    news=PNews.objects.get(id=news_id)
    return render(request,"hod_template/edit_pnews_template.html",{"news":news,"admin":admin})

def edit_pnews_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        news_id=request.POST.get("news_id")
        ntitle=request.POST.get("ntitle")
        ntext=request.POST.get("ntext")
        if request.FILES.get('pic',False):
            pic=request.FILES['pic']
            fs=FileSystemStorage()
            filename=fs.save(pic.name,pic)
            pic_url=fs.url(filename)
        else:
            pic_url=None
        try:
            mv=PNews.objects.get(id=news_id)
            mv.ntitle=ntitle
            mv.ntext=ntext
            if pic_url!=None:
                mv.pic=pic_url
            mv.save()
            messages.success(request,"Мэдээ амжилттай заслаа")
            return HttpResponseRedirect(reverse("manage_pnews"))
        except:
            messages.error(request,"Мэдээ засахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_pnews"))

def delete_pnews(request,news_id):
    if request.method!="GET":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            mv=PNews.objects.get(id=news_id)
            mv.delete()
            messages.success(request,"Мэдээ амжилттай устгалаа")
            return HttpResponseRedirect(reverse("manage_pnews"))
        except:
            messages.error(request,"Мэдээ устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("manage_pnews"))

# POST TEACHER COMMENT
def view_parent_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("manage_pnews"))
    else:
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = PComment.objects.get(id=reply_id)
        try:
            Pcomment=PComment(PNews_id=News, staff_id=staff, body=body, count=a, reply=comment_qs)
            Pcomment.save()
            messages.success(request, "Сэтгэгдэл нэмэгдлээ!")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":News}))
        except:
            messages.error(request, "Сэтгэгдэл нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":News}))
# EDIT TEACHER COMMENT
def view_parent_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("manage_pnews"))
    else:
        comment_id = request.POST.get("comment_id")
        TNews = request.POST.get("News_id")
        body = request.POST.get("body")
        try:
            comment = PComment.objects.get(id=comment_id)
            comment.PNews_id=TNews
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Сэтгэгдэл засагдлаа!")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":TNews}))
        except:
            messages.error(request, "Сэтгэгдэл засахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":TNews}))

def delete_pcomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=PComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Сэтгэгдэл амжилттай устгалаа")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Сэтгэгдэл устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_pnews",kwargs={"news_id":news_id}))

@csrf_exempt
def send_student_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    student=Students.objects.get(admin=id)
    token=student.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"School Management System",
            "body":message,
            "click_action": "https://studentmanagementsystem22.herokuapp.com/student_all_notification",
            "icon": "http://studentmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationStudent(student_id=student,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

@csrf_exempt
def send_staff_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    staff=Staffs.objects.get(admin=id)
    token=staff.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"School Management System",
            "body":message,
            "click_action":"https://studentmanagementsystem22.herokuapp.com/staff_all_notification",
            "icon":"http://studentmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationStaffs(staff_id=staff,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

@csrf_exempt
def send_parent_notification(request):
    id=request.POST.get("id")
    message=request.POST.get("message")
    parent=Parents.objects.get(admin=id)
    token=parent.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"School Management System",
            "body":message,
            "click_action":"https://studentmanagementsystem22.herokuapp.com/parent_all_notification",
            "icon":"http://studentmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification=NotificationParents(parent_id=parent,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

def covid19(request):
    user=CustomUser.objects.get(id=request.user.id)
    admin=AdminHOD.objects.get(admin=user)
    return render(request,"hod_template/covid19.html",{"admin":admin})