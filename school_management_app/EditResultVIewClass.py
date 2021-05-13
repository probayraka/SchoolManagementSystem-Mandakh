from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from school_management_app.forms import EditResultForm
from school_management_app.models import Students, Subjects, StudentResult, CustomUser, Staffs


class EditResultViewClass(View):
    def get(self,request,*args,**kwargs):
        staff_id=request.user.id
        edit_result_form=EditResultForm(staff_id=staff_id)
        user=CustomUser.objects.get(id=request.user.id)
        staff_pro=Staffs.objects.get(admin=user)
        return render(request,"staff_template/edit_student_result.html",{"form":edit_result_form,"staff_pro":staff_pro})

    def post(self,request,*args,**kwargs):
        form=EditResultForm(staff_id=request.user.id,data=request.POST)
        if form.is_valid():
            student_admin_id = form.cleaned_data['student_ids']
            assignment_marks = form.cleaned_data['assignment_marks']
            exam_marks = form.cleaned_data['exam_marks']
            subject_id = form.cleaned_data['subject_id']

            student_obj = Students.objects.get(admin=student_admin_id)
            subject_obj = Subjects.objects.get(id=subject_id)
            result=StudentResult.objects.get(subject_id=subject_obj,student_id=student_obj)
            result.subject_assignment_marks=assignment_marks
            result.subject_exam_marks=exam_marks
            result.save()
            messages.success(request, "Successfully Updated Result")
            return HttpResponseRedirect(reverse("edit_student_result"))
        else:
            messages.error(request, "Failed to Update Result")
            form=EditResultForm(request.POST,staff_id=request.user.id)
            return render(request,"staff_template/edit_student_result.html",{"form":form})


