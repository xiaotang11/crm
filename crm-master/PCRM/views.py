from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


#登录
def account_login(request):
    errors = {}
    if request.method == "POST":
        _email = request.POST.get('email')
        _password = request.POST.get('password')

        user = authenticate(username = _email,password=_password)#直接调用Django的认证方式,认证通过会有返回值
        if user:
            login(request,user)#直接调用Django的登录方法,同时也会创建session
            return redirect('/crm/')
        else:
            errors['登录失败']='用户名或密码错误'

    return render(request,'login.html',{'errors':errors})

#登出
def account_logout(request):

    logout(request)#登出
    return redirect('/account/login/')

def index(request):#全局的index，不同角色看到的页面不一样
    return render(request,'index.html')