import datetime

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

from school_management_app.models import Students, Courses, Subjects, CustomUser, Attendance, AttendanceReport, StudentResult, SessionYearModel, News, SComment, Parents, FeedBackParents, NotificationParents, PNews, PComment

def parent_home(request):
    parent=Parents.objects.get(admin=request.user.id)
    parent_student=parent.student_id
    # student_obj=Students.objects.get(admin=parent_student)
    attendance_total=AttendanceReport.objects.filter(student_id=parent_student).count()
    attendance_present=AttendanceReport.objects.filter(student_id=parent_student,status=True).count()
    attendance_absent=AttendanceReport.objects.filter(student_id=parent_student,status=False).count()
    course=Courses.objects.get(id=parent_student.course_id.id)
    subjects=Subjects.objects.filter(course_id=course).count()

    subject_name=[]
    data_present=[]
    data_absent=[]
    subject_data=Subjects.objects.filter(course_id=parent_student.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=True,student_id=parent_student.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=False,student_id=parent_student.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

    user=CustomUser.objects.get(id=request.user.id)
    parent=Parents.objects.get(admin=user)
    parent_notifcation=Parents.objects.get(admin=request.user.id)
    notifications=NotificationParents.objects.filter(parent_id=parent_notifcation.id)
    return render(request,"parent_template/parent_home_template.html",{"parent":parent,"notifications":notifications,"total_attendance":attendance_total,"attendance_absent":attendance_absent,"attendance_present":attendance_present,"subjects":subjects,"data_name":subject_name,"data1":data_present,"data2":data_absent})

def parent_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    parent=Parents.objects.get(admin=user)
    parent_notifcation=Parents.objects.get(admin=request.user.id)
    notifications=NotificationParents.objects.filter(parent_id=parent_notifcation.id)
    return render(request,"parent_template/parent_profile.html",{"user":user,"parent":parent,"notifications":notifications})

def parent_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("parent_profile"))
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
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()
            parent=Parents.objects.get(admin=customuser)
            if profile_pic_url!=None:
                parent.profile_pic=profile_pic_url
            parent.save()
            messages.success(request, "Мэдээлэл шинэчлэгдлээ")
            return HttpResponseRedirect(reverse("parent_profile"))
        except:
            messages.error(request, "Мэдээлэл шинэчлэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("parent_profile"))

def parent_feedback(request):
    parent_id=Parents.objects.get(admin=request.user.id)
    feedback_data=FeedBackParents.objects.filter(parent_id=parent_id)
    user=CustomUser.objects.get(id=request.user.id)
    parent=Parents.objects.get(admin=user)
    parent_notifcation=Parents.objects.get(admin=request.user.id)
    notifications=NotificationParents.objects.filter(parent_id=parent_notifcation.id)
    return render(request,"parent_template/parent_feedback.html",{"feedback_data":feedback_data,"parent":parent,"notifications":notifications})

def parent_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("parent_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        parent_obj=Parents.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackParents(parent_id=parent_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Санал хүсэлт амжилттай илгээлээ")
            return HttpResponseRedirect(reverse("parent_feedback"))
        except:
            messages.error(request, "Санал хүсэлт илгээхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("parent_feedback"))

def parent_news(request):
    news=PNews.objects.all().order_by('-ndate')
    user=CustomUser.objects.get(id=request.user.id)
    parent=Parents.objects.get(admin=user)
    parent_notifcation=Parents.objects.get(admin=request.user.id)
    notifications=NotificationParents.objects.filter(parent_id=parent_notifcation.id)
    return render(request, "parent_template/parent_news.html",{"news":news,"parent":parent,"notifications":notifications})

def view_parent_news(request, news_id):
    news=PNews.objects.get(id=news_id)
    user=CustomUser.objects.get(id=request.user.id)
    parent=Parents.objects.get(admin=user)
    comment=PComment.objects.filter(PNews=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    parent_notifcation=Parents.objects.get(admin=request.user.id)
    notifications=NotificationParents.objects.filter(parent_id=parent_notifcation.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request, "parent_template/view_parent_news.html",{"news":news,"notifications":notifications,"parent":parent,"comment":comment,"comment_count":comments_count,"staff":staff})

    # Comment
def view_parent_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("parent_news"))
    else:
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = PComment.objects.get(id=reply_id)
        try:
            comment=PComment(PNews_id=News, staff_id=staff, body=body, count=a, reply=comment_qs)
            comment.save()
            messages.success(request, "Сэтгэгдэл нэмэгдлээ!")
            return HttpResponseRedirect(reverse("view_parent_news",kwargs={"news_id":News}))
        except:
            messages.error(request, "Сэтгэгдэл нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_parent_news",kwargs={"news_id":News}))
# EDIT
def view_parent_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("parent_news"))
    else:
        comment_id = request.POST.get("comment_id")
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        try:
            comment = PComment.objects.get(id=comment_id)
            comment.PNews_id=News
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Сэтгэгдэл засагдлаа!")
            return HttpResponseRedirect(reverse("view_parent_news",kwargs={"news_id":News}))
        except:
            messages.error(request, "Сэтгэгдэл засахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_parent_news",kwargs={"news_id":News}))


def delete_pcomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=PComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Сэтгэгдэл амжилттай устгалаа")
            return HttpResponseRedirect(reverse("view_parent_news",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Сэтгэгдэл устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_parent_news",kwargs={"news_id":news_id}))

def parent_all_notification(request):
    parent=Parents.objects.get(admin=request.user.id)
    notifications=NotificationParents.objects.filter(parent_id=parent.id)
    user=CustomUser.objects.get(id=request.user.id)
    parent=Parents.objects.get(admin=user)
    return render(request,"parent_template/all_notification.html",{"notifications":notifications,"parent":parent})

def parent_student_view_result(request):
    parent=Parents.objects.get(admin=request.user.id)
    parent_student=parent.student_id
    studentresult=StudentResult.objects.filter(student_id=parent_student)

    user=CustomUser.objects.get(id=request.user.id)
    parent=Parents.objects.get(admin=user)

    parent_notifcation=Parents.objects.get(admin=request.user.id)
    notifications=NotificationParents.objects.filter(parent_id=parent_notifcation.id)
    return render(request,"parent_template/parent_student_result.html",{"studentresult":studentresult,"parent":parent,"notifications":notifications})

@csrf_exempt
def parent_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        parent=Parents.objects.get(admin=request.user.id)
        parent.fcm_token=token
        parent.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def parent_view_attendance(request):
    parent=Parents.objects.get(admin=request.user.id)
    # student=Students.objects.get(id=parent)
    course=parent.student_id.course_id
    subjects=Subjects.objects.filter(course_id=course)
    user=CustomUser.objects.get(id=request.user.id)
    parent=Parents.objects.get(admin=user)

    parent_notifcation=Parents.objects.get(admin=request.user.id)
    notifications=NotificationParents.objects.filter(parent_id=parent_notifcation.id)
    return render(request,"parent_template/parent_view_attendance.html",{"subjects":subjects,"parent":parent,"notifications":notifications})

def parent_view_attendance_post(request):
    
    subject_id=request.POST.get("subject")
    start_date=request.POST.get("start_date")
    end_date=request.POST.get("end_date")

    parent=Parents.objects.get(admin=request.user.id)
    parent_student=parent.student_id
    start_data_parse=datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_data_parse=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()

    subject_obj=Subjects.objects.get(id=subject_id)

    # user=CustomUser.objects.get(id=request.user.id)
    # parent_pic=Parents.objects.get(admin=user)

    parent_notifcation=Parents.objects.get(admin=request.user.id)
    notifications=NotificationParents.objects.filter(parent_id=parent_notifcation.id)

    attendance=Attendance.objects.filter(attendance_date__range=(start_data_parse,end_data_parse),subject_id=subject_obj)
    attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=parent_student)

    return render(request,"parent_template/parent_student_attendance_data.html",{"attendance_reports":attendance_reports,"parent":parent,"notifications":notifications})


def pcovid19(request):
    user=CustomUser.objects.get(id=request.user.id)
    parent=Parents.objects.get(admin=user)
    parent_notifcation=Parents.objects.get(admin=request.user.id)
    notifications=NotificationParents.objects.filter(parent_id=parent_notifcation.id)
    return render(request,"parent_template/covid19.html",{"parent":parent,"notifications":notifications})