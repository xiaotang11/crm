from django.http import HttpResponse
from django.shortcuts import redirect, render

from crm import models

enabled_admins ={}#定义注册了哪些app，来展示
# 将其构造成样式{'crm':
#                     {'Customer':'',
#                     'Consultant':''}
#                  'student':{},}

'''定义一个基类，便于以后操作
不管子类写不写display和filter，前端依然可以找到他们，只不过为空'''
class BaseAdmin(object):
    list_display = []
    list_filter = []
    list_per_page = 20
    search_fields = []
    ordering = None#排序字段
    actions = ["delete_selected_objs",]
    readonly_fields = []#只读的字段，即不能修改的字段
    readonly_table = False#设置是否是只读的表单
    modelform_exclude_fields = []#修改页面不显示那些字段

    def delete_selected_objs(self,request,querysets):
        #self就是传过来的admin_class
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name
        print("--->delete_selected_objs",self,request,querysets)
        if self.readonly_table:
            errors = {"只读表": "不能被删除" }
        else:
            errors = {}
        if request.POST.get("delete_confirm") == "yes":#第二次post过来，是删除页面的post，即确认删除
            if not self.readonly_table:
                querysets.delete()
                return redirect("/king_admin/%s/%s/" % (app_name,table_name))

        selected_ids =  ','.join([str(i.id) for i in querysets])#将id拿出来，以逗号来分割，拼接起来  3,4
        return render(request,"king_admin/table_obj_delete.html",{"objs":querysets,
                                                              "admin_class":self,
                                                              "app_name": app_name,
                                                              "table_name": table_name,
                                                              "selected_ids":selected_ids,
                                                              "action":request._admin_action, #从reques里面取之前放进来的这个action
                                                              'errors':errors
                                                                  })

    delete_selected_objs.display_name = "批量删除"

    def default_form_validation(self):
        '''用户可以在此进行自定义的表单验证，相当于django form的clean方法'''
        pass

'''定义子类'''
class CustomerAdmin(BaseAdmin):
    list_display = ['id','qq','name','status','source','consultant','date','enroll']
    #enroll不是数据库里的字段，但是想在前端显示，所以定义了enroll函数，并在前端的自定义标签中，接收FieldDoesNotExist 错误，有错误时，调用该函数
    #model = models.Customer直接在register函数里面定义这个属性也是可以的,将其和表关联起来
    list_filter = ['source','consultant','consult_course','status','date']
    list_per_page = 5
    search_fields = ['qq','name']
    ordering = ['qq']
    actions = ["delete_selected_objs","testtest"]
    readonly_fields = ['qq','consultant']
    # readonly_table = True
    readonly_table = False

    def testtest(self):
        print('testtest')
    testtest.display_name = "测试动作"

    def enroll(self):
        # print("enroll",self.instance)
        if self.instance.status ==0:#说明已经报了课程了
            link_name = "报名新课程"
        else:
            link_name = "报名"
        return '''<a href="/crm/customer/%s/enrollment/" > %s</a>''' %(self.instance.id,link_name)
    enroll.display_name = "报名链接"

    # def enroll(self):
    #     # print(self.instance.id)#这个instance是tag.py里面调用时传的，self 指代admin——class
    #     return '''<a href="/crm/customer/%s/enrollment/">报名连接</a>'''%self.instance.id
    # enroll.display_name ="报名链接"

class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['customer','consultant','date']

class UserProfileAdmin(BaseAdmin):
    list_display = ['email','name','is_admin','is_active']
    readonly_fields = ['password']
    modelform_exclude_fields = ['last_login']

class CourseRecordAdmin(BaseAdmin):
    list_display = ['from_class','day_num','teacher','has_homework','homework_title','date']

    def initialize_studyrecords(self, request, queryset):
        print('--->initialize_studyrecords',self,request,queryset)
        if len(queryset) > 1:   #不能选多个班级
            return HttpResponse("只能选择一个班级")

        # print(queryset[0].from_class.enrollment_set.all())
        new_obj_list = []
        for enroll_obj in queryset[0].from_class.enrollment_set.all():#找到此课程所有报了名的学生
            # models.StudyRecord.objects.get_or_create(     #get_or_create（）有就获取，没有就创建
            #     student = enroll_obj,
            #     course_record = queryset[0] ,
            #     attendance = 0 ,
            #     score = 0 ,
            # ) #但这样新增效率低！！

            new_obj_list.append(models.StudyRecord(
                student = enroll_obj,
                course_record = queryset[0] ,#课程记录
                attendence = 0 ,#状态，迟到还是早退
                score = 0 ,#分数
            ))

        try:
            models.StudyRecord.objects.bulk_create(new_obj_list) #批量创建（高效）
        except Exception:
            return HttpResponse("批量初始化学习记录失败，请检查该节课是否已经有对应的学习记录")
        return redirect("/king_admin/crm/studyrecord/?course_record=%s"%queryset[0].id )

    initialize_studyrecords.display_name = "初始化本节所有学员的上课记录"
    actions = ['initialize_studyrecords',]
# 自定制action！！

class StudyRecordAdmin(BaseAdmin):
    list_display = ['student','course_record','attendance','score','date']
    list_filters = ['course_record','score','attendance']
    list_editable = ['score','attendance']

def register(model_class,admin_class=None):
    '''定义注册函数'''
    '''model_class._meta.app_label可以获取到app的名字
    如：models.UserProfile.._meta.app_label===>'crm'
    '''
    app_name = model_class._meta.app_label #app的 name
    table_name = model_class._meta.model_name #表名
    if app_name not in enabled_admins:
        enabled_admins[app_name] = {}

    admin_class.model = model_class #给admin_class加一个属性,通过添加属性的方式，动态的将register注册的表和其配置表关联起来
    enabled_admins[app_name][table_name] = admin_class


register(models.Customer,CustomerAdmin)
register(models.CustomerFollowUp,CustomerFollowUpAdmin)

register(models.UserProfile,UserProfileAdmin)

register(models.CourseRecord,CourseRecordAdmin)#上课记录
register(models.StudyRecord,StudyRecordAdmin)#学习记录


