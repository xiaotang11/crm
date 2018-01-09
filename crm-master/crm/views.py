import random
import string

import os
from django.core.cache import cache
from django.db import IntegrityError
from django.http import HttpResponse

from django.shortcuts import render, redirect

# Create your views here.
from PCRM import settings
from crm import forms, models


def index(request):
    return render(request,'index.html')

def customer_list(request):
    return render(request,'sales/customers.html')
#注意是在sales文件夹中！！！

#报名表
def enrollment(request,customer_id):

    customer_obj = models.Customer.objects.get(id = customer_id)#拿到该用户
    msgs = {}
    enroll_form = forms.EnrollmentForm()
    if request.method =='POST':
        enroll_form = forms.EnrollmentForm(request.POST)
        if enroll_form.is_valid():
            msg = '''请将此链接发送给客户进行填写:
                http://localhost:8001/crm/customer/registration/{enroll_obj_id}/{random_str}/'''
            try:
                enroll_form.cleaned_data["customer"] = customer_obj  # 将用户信息单独加到form里面，因为只能给当前用户报名，不能临时切换成其他用户
                enroll_obj = models.Enrollment.objects.create(**enroll_form.cleaned_data)
                msgs["msg"] = msg.format(enroll_obj_id=enroll_obj.id)#创建成功后，把连接给用户，让其上传照片什么的

            except IntegrityError as e:  # 此错误是因为联合唯一错误，说明此用户已经报了该课程了
                enroll_obj = models.Enrollment.objects.get(customer_id=customer_obj.id,
                                                           enrolled_class_id=enroll_form.cleaned_data[
                                                               "enrolled_class"].id)
                # 拿到该用户
                enroll_form.add_error("__all__", "该用户的此条报名信息已存在，不能重复创建")

                random_str = "".join(random.sample(string.ascii_lowercase + string.digits, 8))
                cache.set(enroll_obj.id, random_str,3000)#给enroll_obj.id设置一个cache，值为random_str，
                # 超时时间为3000s，这样用户报名的网址就每次都不一样
                msgs["msg"] = msg.format(enroll_obj_id=enroll_obj.id, random_str=random_str)

    return render(request,'sales/enrollment.html',{'enroll_form':enroll_form,
                                                   'customer_obj':customer_obj,
                                                   'msgs':msgs})

#学生填写报名信息页面
# def stu_registration(request,enroll_id):
#     enroll_obj = models.Enrollment.objects.get(id=enroll_id)
#     customer_form = forms.CustomerForm(request.POST, instance=enroll_obj.customer)
#
#     return render(request, "sales/stu_registration.html",
#                   {"customer_form": customer_form,
#                    "enroll_obj": enroll_obj})

#学生填写信息页面

#学生填写表单
def stu_registration(request,enroll_id,random_str):
    if True :# cache.get(enroll_id) == random_str:#如果cache里面拿到的哪个id和网址上返回来的random_str一直，说明使我们
        # 自己生成的，否则就是想黑我们
        status = 0
        enroll_obj = models.Enrollment.objects.get(id=enroll_id)
        if request.method == "POST":#提交表单

            if request.is_ajax():
                #如果是ajax请求，即上传身份证照片
                print("ajax post, ", request.FILES)
                enroll_data_dir = "%s/%s" %(settings.ENROLLED_DATA,enroll_id)#创建文件夹
                if not os.path.exists(enroll_data_dir):#如果该文件夹不存在
                    os.makedirs(enroll_data_dir,exist_ok=True)#创建文件夹，如果文件夹已存在，就不在重复创建

                for k,file_obj in request.FILES.items():#从request中取到此文件对象
                    with open("%s/%s"%(enroll_data_dir, file_obj.name), "wb") as f:#打开这个文件夹
                        for chunk in file_obj.chunks():#将request中取到的文件写入文件夹，以chunks方式
                            f.write(chunk)

                return HttpResponse("success")

            customer_form = forms.CustomerForm(request.POST,instance=enroll_obj.customer)#更新
            if customer_form.is_valid():#格式正确，字段也没有被修改
                customer_form.save()
                enroll_obj.contract_agreed = True#手动将数据库中的  学员已同意合同  属性改为真
                enroll_obj.save()
                return render(request,"sales/stu_registration.html",{"status":1})
        else:#get 请求
            if enroll_obj.contract_agreed == True:#如果该学员已经提交合同
                status =  1
            else:
                status =  0
            customer_form = forms.CustomerForm(instance=enroll_obj.customer)
        return  render(request,"sales/stu_registration.html",
                       {"customer_form":customer_form,
                        "enroll_obj":enroll_obj,
                        "status":status})

    else:   #random_str 不一致时
        return HttpResponse("去死,还想黑我")


#返回学员信息审核页面
def contract_review(request,enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_form = forms.EnrollmentForm(instance=enroll_obj)
    customer_form = forms.CustomerForm(instance=enroll_obj.customer)
    return render(request, 'sales/contract_review.html', {
                                                "enroll_obj":enroll_obj,
                                                "enroll_form":enroll_form,
                                                'customer_form':customer_form})

#返回缴费信息页面
def payment(request,enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    errors = []
    if request.method == "POST":
        payment_amount = request.POST.get("amount")
        if payment_amount:
            payment_amount = int(payment_amount)

            if payment_amount < 500:
                errors.append("缴费金额不得低于500元")
            else:#新增缴费记录
                payment_obj = models.Payment.objects.create(
                    customer= enroll_obj.customer,
                    course = enroll_obj.enrolled_class.course,
                    amount = payment_amount,
                    consultant = enroll_obj.consultant
                )
                enroll_obj.contract_approved = True #合同已审核属性 改为真
                enroll_obj.save()


                enroll_obj.customer.status = 0
                enroll_obj.customer.save()
                return redirect("/king_admin/crm/customer/")
        else:
            errors.append("缴费金额不得低于500元")
    print("errors",errors)
    return render(request,"sales/payment.html",{'enroll_obj':enroll_obj,
                                                'errors':errors})


#审核驳回页面
def enrollment_rejection(request,enroll_id):

    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_obj.contract_agreed = False #学员已同意合同属性 改为假
    enroll_obj.save()

    return  redirect("/crm/customer/%s/enrollment/" %enroll_obj.customer.id)
