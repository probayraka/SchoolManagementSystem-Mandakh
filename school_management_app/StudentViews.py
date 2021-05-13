import datetime

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

from school_management_app.models import Students, Courses, Subjects, CustomUser, Attendance, AttendanceReport, \
    LeaveReportStudent, FeedBackStudent, NotificationStudent, StudentResult, OnlineClassRoom, SessionYearModel, News, SComment


def student_home(request):
    student_obj=Students.objects.get(admin=request.user.id)
    attendance_total=AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present=AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    attendance_absent=AttendanceReport.objects.filter(student_id=student_obj,status=False).count()
    course=Courses.objects.get(id=student_obj.course_id.id)
    subjects=Subjects.objects.filter(course_id=course).count()
    subjects_data=Subjects.objects.filter(course_id=course)
    session_obj=SessionYearModel.object.get(id=student_obj.session_year_id.id)
    class_room=OnlineClassRoom.objects.filter(subject__in=subjects_data,is_active=True,session_years=session_obj)
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)

    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)

    subject_name=[]
    data_present=[]
    data_absent=[]
    subject_data=Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=True,student_id=student_obj.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=False,student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

    return render(request,"student_template/student_home_template.html",{"notifications":notifications,"total_attendance":attendance_total,"attendance_absent":attendance_absent,"attendance_present":attendance_present,"subjects":subjects,"data_name":subject_name,"data1":data_present,"data2":data_absent,"class_room":class_room,"student":student})

def join_class_room(request,subject_id,session_year_id):
    session_year_obj=SessionYearModel.object.get(id=session_year_id)
    subjects=Subjects.objects.filter(id=subject_id)
    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)
    if subjects.exists():
        session=SessionYearModel.object.filter(id=session_year_obj.id)
        if session.exists():
            subject_obj=Subjects.objects.get(id=subject_id)
            course=Courses.objects.get(id=subject_obj.course_id.id)
            check_course=Students.objects.filter(admin=request.user.id,course_id=course.id)
            if check_course.exists():
                session_check=Students.objects.filter(admin=request.user.id,session_year_id=session_year_obj.id)
                if session_check.exists():
                    onlineclass=OnlineClassRoom.objects.get(session_years=session_year_id,subject=subject_id)
                    return render(request,"student_template/join_class_room_start.html",{"username":request.user.username,"password":onlineclass.room_pwd,"roomid":onlineclass.room_name,"notifications":notifications})

                else:
                    return HttpResponse("This Online Session is Not For You")
            else:
                return HttpResponse("This Subject is Not For You")
        else:
            return HttpResponse("Session Year Not Found")
    else:
        return HttpResponse("Subject Not Found")


def student_view_attendance(request):
    student=Students.objects.get(admin=request.user.id)
    course=student.course_id
    subjects=Subjects.objects.filter(course_id=course)
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)
    return render(request,"student_template/student_view_attendance.html",{"subjects":subjects,"student":student,"notifications":notifications})

def student_view_attendance_post(request):
    subject_id=request.POST.get("subject")
    start_date=request.POST.get("start_date")
    end_date=request.POST.get("end_date")

    start_data_parse=datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_data_parse=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
    subject_obj=Subjects.objects.get(id=subject_id)
    user_object=CustomUser.objects.get(id=request.user.id)
    stud_obj=Students.objects.get(admin=user_object)
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)

    attendance=Attendance.objects.filter(attendance_date__range=(start_data_parse,end_data_parse),subject_id=subject_obj)
    attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=stud_obj)
    return render(request,"student_template/student_attendance_data.html",{"attendance_reports":attendance_reports,"student":student,"notifications":notifications})

def student_apply_leave(request):
    staff_obj = Students.objects.get(admin=request.user.id)
    leave_data=LeaveReportStudent.objects.filter(student_id=staff_obj)
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)
    return render(request,"student_template/student_apply_leave.html",{"leave_data":leave_data,"student":student,"notifications":notifications})

def student_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportStudent(student_id=student_obj,leave_date=leave_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Чөлөөний хүсэлт амжилттай илгээлээ")
            return HttpResponseRedirect(reverse("student_apply_leave"))
        except:
            messages.error(request, "Хүсэлт илгээхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("student_apply_leave"))


def student_feedback(request):
    staff_id=Students.objects.get(admin=request.user.id)
    feedback_data=FeedBackStudent.objects.filter(student_id=staff_id)
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)
    return render(request,"student_template/student_feedback.html",{"feedback_data":feedback_data,"student":student,"notifications":notifications})

def student_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStudent(student_id=student_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Санал хүсэлт амжилттай илгээлээ")
            return HttpResponseRedirect(reverse("student_feedback"))
        except:
            messages.error(request, "Санал хүсэлт илгээхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("student_feedback"))

def student_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)
    return render(request,"student_template/student_profile.html",{"user":user,"student":student,"notifications":notifications})

def student_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        address=request.POST.get("address")
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
            student=Students.objects.get(admin=customuser)
            student.address=address
            if profile_pic_url!=None:
                student.profile_pic=profile_pic_url
            student.save()
            messages.success(request, "Мэдээлэл шинэчлэгдлээ")
            return HttpResponseRedirect(reverse("student_profile"))
        except:
            messages.error(request, "Мэдээлэл шинэчлэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("student_profile"))

def student_news(request):
    news=News.objects.all().order_by('-ndate')
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)
    return render(request, "student_template/student_news.html",{"news":news,"student":student,"notifications":notifications})

def view_student_news(request, news_id):
    news=News.objects.get(id=news_id)
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    comment=SComment.objects.filter(News=news_id, reply=None).order_by('-id')
    staff=CustomUser.objects.get(id=request.user.id)
    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)
    comments_count = 0
    for b in comment:
        comments_count += b.count
    return render(request, "student_template/view_student_news.html",{"news":news,"notifications":notifications,"student":student,"comment":comment,"comment_count":comments_count,"staff":staff})

# Comment
def view_student_news_comment_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_news"))
    else:
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        reply_id = request.POST.get('comment_id')
        comment_qs = None
        if reply_id:
            comment_qs = SComment.objects.get(id=reply_id)
        try:
            comment=SComment(News_id=News, staff_id=staff, body=body, count=a, reply=comment_qs)
            comment.save()
            messages.success(request, "Сэтгэгдэл нэмэгдлээ!")
            return HttpResponseRedirect(reverse("view_student_news",kwargs={"news_id":News}))
        except:
            messages.error(request, "Сэтгэгдэл нэмэхэд алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_student_news",kwargs={"news_id":News}))
# EDIT
def view_student_news_comment_edit_save(request):
    a = 1
    staff=CustomUser.objects.get(id=request.user.id)

    if request.method!="POST":
        messages.error(request, "Method not allowed!")
        return HttpResponseRedirect(reverse("student_news"))
    else:
        comment_id = request.POST.get("comment_id")
        News = request.POST.get("News_id")
        body = request.POST.get("body")
        try:
            comment = SComment.objects.get(id=comment_id)
            comment.News_id=News
            comment.staff_id=staff
            comment.body=body
            comment.count=a
            comment.save()
            messages.success(request, "Сэтгэгдэл засагдлаа!")
            return HttpResponseRedirect(reverse("view_student_news",kwargs={"news_id":News}))
        except:
            messages.error(request, "Сэтгэгдэл засахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_student_news",kwargs={"news_id":News}))


def delete_scomment(request,comment_id,news_id):
    if request.method!="GET":
            return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        try:
            a=SComment.objects.get(id=comment_id)
            a.delete()
            messages.success(request,"Сэтгэгдэл амжилттай устгалаа")
            return HttpResponseRedirect(reverse("view_student_news",kwargs={"news_id":news_id}))
        except:
            messages.error(request,"Сэтгэгдэл устгахад алдаа гарлаа")
            return HttpResponseRedirect(reverse("view_student_news",kwargs={"news_id":news_id}))

@csrf_exempt
def student_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        student=Students.objects.get(admin=request.user.id)
        student.fcm_token=token
        student.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def student_all_notification(request):
    student=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student.id)
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    return render(request,"student_template/all_notification.html",{"notifications":notifications,"student":student})

def student_view_result(request):
    student=Students.objects.get(admin=request.user.id)
    studentresult=StudentResult.objects.filter(student_id=student.id)
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)
    return render(request,"student_template/student_result.html",{"studentresult":studentresult,"student":student,"notifications":notifications})

def scovid19(request):
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    student_notifcation=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student_notifcation.id)
    return render(request,"student_template/covid19.html",{"student":student,"notifications":notifications})