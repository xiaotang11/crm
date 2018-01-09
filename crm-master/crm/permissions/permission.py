#__author:  Administrator
#自定义验证
from  crm.permissions import permission_list  #将权限列表导入进来
from django.core.urlresolvers import resolve
from django.shortcuts import HttpResponse, render, redirect

def perm_check(*args,**kwargs):
    request= args[0]
    print("request path:",request.path )
    if request.user.is_authenticated(): #如果用户登录了
        for permission_name, v in permission_list.perm_dic.items():
            # print(permission_name, v) #字典中的权限名称，及对应权限 如 crm.can_access_my_course   {'url_type': 0, 'url': 'stu_my_classes', 'method': 'GET', 'args': []}
            url_matched =  False
            if v['url_type'] == 1: #字典中url为绝对地址
                if v['url'] == request.path: #绝对url匹配上了  '/king_admin/crm/customer/'
                    url_matched = True
            else:#字典中url为相对地址   'stu_my_classes'
                #把request中的绝对url请求转成相对的url name
                resolve_url_obj = resolve(request.path)
                print('resolve_url_obj',resolve_url_obj)
                if resolve_url_obj.url_name == v['url']:#相对的url 别名匹配上了
                    url_matched = True

            if url_matched:
                print("url  matched...")
                if v['method'] == request.method: #请求方法也匹配上了
                    arg_matched = True
                    for request_arg in v['args']:  #[]
                        request_method_func = getattr(request,v['method'])#   request_method_func= request.GET
                        print('------->request_method_func.get(request_arg)',request_method_func.get(request_arg))
                        if not request_method_func.get(request_arg):# request.GET来取arg中的参数，如果没有，则参数不匹配，没有权限
                            arg_matched = False

                    if arg_matched:#走到这里，仅代表这个请求 和这条权限的定义规则 匹配上了
                        print("arg  matched...")
                        if request.user.has_perm(permission_name):
                            #有权限
                            print("有权限",permission_name)#如 crm.can_access_my_course
                            return True


    else:
        return redirect("/account/login/")


def check_permission(func):
    print('--------check_permission')
    def inner(*args,**kwargs):
        print("--permission:" ,*args,**kwargs)#--permission: <WSGIRequest: GET '/king_admin/crm/customer/'> crm customer
        print("--func:",func)#--func: <function display_table_objs at 0x02F37A50>
        if perm_check(*args,**kwargs) is True:#即有此权限
            return func(*args,**kwargs) # display_table_objs（）
        else:
            return HttpResponse("没权限")

    return inner
