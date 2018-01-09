
from django.conf.urls import url
from crm import views

urlpatterns = [
    url(r'^$', views.index,name="sales_index"),
    url(r'^customers/$', views.customer_list,name="customer_list"),
    url(r'^customer/(\d+)/enrollment/$', views.enrollment,name="enrollment"),
    #取别名，不管网址如何变，前端都可以通过这个name来映射它！！！
    url(r'^customer/registration/(\d+)/(\w+)/', views.stu_registration,name="stu_registration"),
    # customer/registration/(\d+)/(\w+)/ 学员注册填写信息页面
    url(r'^contract_review/(\d+)/', views.contract_review, name="contract_review"),
    # 信息审核页面
    url(r'^payment/(\d+)/', views.payment, name="payment"),
    # payment 缴费页面
    url(r'^enrollment_rejection/(\d+)/', views.enrollment_rejection, name="enrollment_rejection"),
    # enrollment_rejection 审核驳回页面

    url(r'^customers/$', views.customer_list, name="customer_list"),

]
