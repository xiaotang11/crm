from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from king_admin import king_admin
# Create your views here.
from king_admin.forms import create_model_form
from king_admin.utils import table_filter, table_search, table_sort

@login_required
def index(request):
    '''print(king_admin.enabled_admins)
    构造好的app  表名  字典{'crm': {'customer': <class 'king_admin.king_admin.CustomerAdmin'>, 'customerfollowup': <class 'king_admin.king_admin.CustomerFollowUpAdmin'>}}
    print(king_admin.enabled_admins['crm']['customer'])
    <class 'king_admin.king_admin.CustomerAdmin'>找到定义的这个类'''
    print(king_admin.enabled_admins['crm']['customer'].model)
    '''<class 'crm.models.Customer'>找到对应的表'''

    return render(request, 'king_admin/table_index.html', {'table_list':king_admin.enabled_admins})

# @permission.check_permission
@login_required#这个装饰器用于检测是否登录，没有登录就不让进
#表内容展示页,显示需要显示的哪些字段，以及各字段对应的内容
def display_table_objs(request,app_name,table_name):
#1、
    admin_class = king_admin.enabled_admins[app_name][table_name]
    #从king_admin里面的字典enabled_admins里面取
    # object_list = admin_class.model.objects.all()

    if request.method == "POST":
# 删除会有两次post，两次post都是新的post，所以每次post都应该带上选中的id和相应的动作
    # 第一次是展示页面的form表单的post提交，即批量操作的action 来了，到delete页面，展示需要删哪些内容，
    # 点确认以后，再来一个POST，是删除页面的form表单的确认删除的post，才删除，删除后返回table展示页面
    #     print(request.POST)
        selected_ids = request.POST.get("selected_ids")  # 拿到选中的id
        action = request.POST.get("action")  # 拿到动作名称
        if selected_ids:
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(','))
        else:
            raise KeyError("No object selected.")
        if hasattr(admin_class, action):
            action_func = getattr(admin_class, action)
            request._admin_action = action  # 将这个action强制放到request里面去
            return action_func(admin_class, request,selected_objs)
            # 跳转到执行动作的函数，即delete_selected_objs（）,但返回的只是delete页面的内容！！！
# 2、过滤字段
    object_list,filter_conditions = table_filter(request,admin_class)
    # print('object_list',object_list)
    # print('filter_conditions',filter_conditions)
#3、搜索
    object_list= table_search(request,admin_class,object_list)
#4、排序
    object_list,orderby_key = table_sort(request,admin_class,object_list)#排序后的结果
#5、分页
    # 分页直接调用Django自带的Paginator
    #https://docs.djangoproject.com/en/1.10/topics/pagination/
    paginator = Paginator(object_list,admin_class.list_per_page)
    page = request.GET.get('page')
    try:
        query_sets = paginator.page(page)
    except PageNotAnInteger:
        query_sets = paginator.page(1)
        #非整数时，返回第一页
    except EmptyPage:
        query_sets = paginator.page(paginator.num_pages)
        #页数小于1或大于最大页数时，返回最大页

    return render(request, 'king_admin/table_objs.html', {'admin_class':admin_class,
                                                          'query_sets':query_sets,
                                                          'filter_condtions':filter_conditions,
                                                          'search_text':request.GET.get("_q",""),
                                                          'orderby_key':orderby_key,

                                                          })

@login_required
#添加信息页面
def table_obj_add(request,app_name,table_name):
    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request,admin_class)
    admin_class.is_add_form = True
    #is_add_form这个属性用在自动生成form表单时，来判断是add页面还是change页面，add页面就不加disabled属性了
    if request.method == "POST":
        form_obj = model_form_class(request.POST)  #
        if form_obj.is_valid():
            form_obj.save()
            return  redirect(request.path.replace("/add/","/"))
            # 即返回到表内容页面，而不是add页面！！！
    else:
        form_obj = model_form_class()

    return render(request, "king_admin/table_obj_add.html", {"form_obj": form_obj})

# @permission.check_permission
@login_required
#修改信息页面
def table_obj_change(request,app_name,table_name,obj_id):
    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request,admin_class)#动态地创建modelform

    obj = admin_class.model.objects.get(id=obj_id)
    if request.method=='POST':
        form_obj = model_form_class(request.POST,instance=obj)#更新该条信息
        if form_obj.is_valid():
            form_obj.save()
    else:
        form_obj = model_form_class(instance=obj)

    return render(request,'king_admin/table_obj_change.html',{"form_obj":form_obj,
                                                              'app_name':app_name,
                                                              'table_name':table_name,
                                                              'obj_id':obj_id,
                                                              'admin_class':admin_class})
    #修改信息以后，还是跳转到此页面显示

@login_required
#单条信息删除页面
def table_obj_delete(request,app_name,table_name,obj_id):
    admin_class = king_admin.enabled_admins[app_name][table_name]

    # obj = admin_class.model.objects.get(id=obj_id)      #object
    obj = admin_class.model.objects.filter(id=obj_id)#queryset
    print('table_obj_delete-----------obj',obj)

    if  admin_class.readonly_table:#如果是readonly表，就添加错误返回
        errors = {"只读表": "该表只能查看，不能删除" }
    else:
        errors = {}

    if request.method =='POST':
        if not admin_class.readonly_table:#如果不是只读的表，就删除
            obj.delete()
            return redirect("/king_admin/%s/%s/" % (app_name, table_name))
    else:
        return render(request, 'king_admin/table_obj_delete.html', {'app_name': app_name,
                                                                    'table_name': table_name,
                                                                    'objs': obj,#应该给他穿个queryset过去
                                                                    "admin_class": admin_class,
                                                                    'errors':errors#将错误信息返回
                                                                    })

@login_required
#修改密码
def password_reset(request,app_name,table_name,obj_id):
    admin_class = king_admin.enabled_admins[app_name][table_name]
    obj = admin_class.model.objects.get(id=obj_id)

    errors =[]
    if request.method == 'POST':
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        if p1 ==p2:
            if len(p1)>5:
                obj.set_password(p1)#更新密码
                obj.save()
                return redirect(request.path.rstrip('password/'))
            else:
                errors['tooshort'] = '密码长度至少6位'
        else:
            errors['invalid'] = '两个密码必须相同'
    return render(request,'king_admin/password_reset.html',{"obj":obj,
                                                            'errors':errors})


@login_required#报名
def enrollment(request,app_name,table_name,obj_id):
    admin_class = king_admin.enabled_admins[app_name][table_name]
    obj = admin_class.model.objects.get(id=obj_id)
    pass




