from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import PermissionsMixin,User  # 此表用于做密码加密用的
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _#国际化

class Customer(models.Model):
    '''客户信息表'''
    name = models.CharField(max_length=32,blank=True,null=True,help_text='请填写真实姓名')
    #blank=True仅适用于Django Admin ，blank和null必须成对出现
    qq = models.CharField(max_length=64,unique=True)
    qq_name = models.CharField(max_length=64,blank=True,null=True)
    phone = models.CharField(max_length=64,blank=True,null=True)
    source_choices = (
                    (0,'转介绍'),
                    (1,'QQ群'),
                    (2,'官网'),
                    (3,'百度推广'),
                    (4,'51CTO'),
                    (5,'知乎'),
                    (6,'市场推广'),
                    )
    source = models.SmallIntegerField(verbose_name='来源',choices=source_choices)
    referral_from = models.CharField(verbose_name='转介绍人qq',max_length=64,blank=True,null=True)

    consult_course = models.ForeignKey('Course',verbose_name='咨询课程')
    content = models.TextField(verbose_name='咨询详情')
    tags = models.ManyToManyField('Tag',blank=True,null=True,verbose_name='客户标签')
    consultant = models.ForeignKey('UserProfile',verbose_name='咨询专家')
    memo = models.TextField(blank=True,null=True,verbose_name='备注')
    date = models.DateTimeField(auto_now_add=True)

    status_choices = ((0, '已报名'),
                      (1, '未报名'),
                      )
    status = models.SmallIntegerField(choices=status_choices, default=1)

    id_num = models.CharField(verbose_name="身份证号",max_length=64, blank=True, null=True)
    email = models.EmailField(verbose_name="常用邮箱", blank=True, null=True)

    def __str__(self):
        return self.qq
    class Meta:
        verbose_name='客户表'#在Django中显示的别名

class Tag(models.Model):
    '''客户标签'''
    name = models.CharField(unique=True,max_length=32)
    def __str__(self):
        return self.name

class CustomerFollowUp(models.Model):
    '''客户跟进表'''
    customer = models.ForeignKey('Customer')
    content = models.TextField(verbose_name='跟进内容')
    consultant= models.ForeignKey('UserProfile',verbose_name='跟进人')

    intention_choices = (
                        (0,'2周内报名'),
                        (1,'1个月内报名'),
                        (2,'近期无报名计划'),
                        (3,'已在其他机构报名'),
                        (4,'已报名'),
                        (5,'已拉黑'),
                         )
    intention = models.SmallIntegerField(choices=intention_choices,verbose_name='报名意向')
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "%s %s"%(self.customer.qq,self.intention)
    class Meta:
        verbose_name='客户跟进表'#在Django中显示的别名

class Course(models.Model):
    '''课程表'''
    name = models.CharField(max_length=64,unique=True)#课程名
    price = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name='周期（月）')
    outline = models.TextField()#大纲

    def __str__(self):
        return self.name

class Branch(models.Model):
    '''校区'''
    name = models.CharField(max_length=128,unique=True)
    addr = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class ClassList(models.Model):
    '''班级表'''
    branch = models.ForeignKey("Branch",verbose_name="校区")#校区
    course = models.ForeignKey("Course")#课程
    class_type_choices = ((0,'面授（脱产）'),
                          (1,'面授（周末）'),
                          (2,'网络班'),
                          )
    class_type = models.SmallIntegerField(choices=class_type_choices,verbose_name="课程类型")
    semester = models.PositiveSmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField("UserProfile")
    start_date = models.DateField(verbose_name="开班日期")
    end_date = models.DateField(verbose_name="结业日期",blank=True,null=True)

    contract = models.ForeignKey("ContractTemplate",blank=True,null=True)#合同

    def __str__(self):
        return "%s %s %s"%(self.branch,self.course,self.semester)
    class Meta:
        unique_together = ('branch','course','semester')

class CourseRecord(models.Model):
    '''上课记录表'''
    from_class = models.ForeignKey("ClassList",verbose_name='班级')
    day_num = models.PositiveSmallIntegerField(verbose_name='第几节（天）')
    teacher = models.ForeignKey('UserProfile')#老师
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=128,blank=True,null=True)
    homework_content = models.TextField(blank=True,null=True)
    outline = models.TextField(verbose_name='本节课程大纲')
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return "%s %s"%(self.from_class,self.day_num)
    class Meta:
        unique_together = ('from_class','day_num')
        verbose_name = '上课记录表'  # 在Django中显示的别名

class StudyRecord(models.Model):
    '''学习记录'''
    student = models.ForeignKey('Enrollment')
    course_record = models.ForeignKey('CourseRecord')
    attendance_choices = ((0,'已签到'),
                          (1,'迟到'),
                          (2,'缺勤'),
                          (3,'早退'),
                          )
    attendance = models.SmallIntegerField(choices=attendance_choices,verbose_name='出勤记录')
    score_choices = ((100, 'A+'),
                      (90, 'A'),
                      (85, 'B+'),
                      (80, 'B'),
                      (75, 'B-'),
                      (70, 'C+'),
                      (60, 'C'),
                      (40, 'C-'),
                      (-50, 'D'),
                      (-100, 'COPY'),
                      (0, 'N/A'),
                    )
    score= models.SmallIntegerField(choices=score_choices,default=0)
    memo = models.TextField(blank=True,null=True,verbose_name='备注')
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return "%s %s %s"%(self.student,self.course_record,self.score)
    class Meta:
        unique_together=('student','course_record')
        verbose_name = '学习记录'

class Enrollment(models.Model):
    '''报名表'''
    customer = models.ForeignKey('Customer')
    enrolled_class = models.ForeignKey('ClassList',verbose_name='所报班级')
    consultant = models.ForeignKey('UserProfile',verbose_name='课程顾问')
    contract_agreed = models.BooleanField(default=False,verbose_name='学员已同意合同')
    contract_approved = models.BooleanField(default=False,verbose_name='合同已审核')
    date = models.DateTimeField(auto_now_add=True)#报名时间
    def __str__(self):
        return "%s %s"%(self.customer,self.enrolled_class)
    class Meta:
        unique_together = ('customer','enrolled_class')

class Payment(models.Model):
    '''缴费记录'''
    customer = models.ForeignKey('Customer')
    course = models.ForeignKey('Course',verbose_name='所报课程')
    amount = models.PositiveIntegerField(verbose_name='缴费数额',default=500)
    consultant = models.ForeignKey('UserProfile',verbose_name='课程顾问')
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "%s %s"%(self.customer,self.amount)

class Role(models.Model):
    '''角色表'''
    name= models.CharField(max_length=32,unique=True)
    menus = models.ManyToManyField('Menu',blank=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '角色'

class Menu(models.Model):
    '''菜单'''
    name= models.CharField(max_length=32)
    url_name = models.CharField(max_length=64)

    url_type_choices = ((0,'相对地址'),(1,'绝对路径'))
    url_type = models.SmallIntegerField(choices=url_type_choices,default=0)
    #url_type用于显示这个url是绝对路径还是相对路径

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural='菜单'

# class UserProfile(models.Model):
#     '''自定义认证之前的账号表'''
#     user = models.OneToOneField(User)#一对一的，我关联了它，别人就不能关联它
#     name = models.CharField(max_length=32)
#     roles = models.ManyToManyField('Role',blank=True,null=True)#角色
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name='账号表'#在Django中显示的别名

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class MyUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser,PermissionsMixin):
    #账号表
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=32)
    password = models.CharField(_('password'), max_length=128,
                                help_text=mark_safe('''<a href='password/'>点我改密码</a>'''))
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    roles = models.ManyToManyField('Role',blank=True)
    objects = MyUserManager()

    stu_account = models.ForeignKey("Customer", verbose_name="关联学员账号", blank=True, null=True,
                                    help_text="只有学员报名后方可为其创建账号")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        verbose_name = '账号表'  # 在Django中显示的别名
        # permissions = (#自定义的权限可以在我们定义model时手动添加：
        #                ('can_access_my_course','可以访问我的课程'),
        #                # codename如上面的can_access_my_course，代码逻辑中检查权限时要用
        #                # 可以访问我的课程 是permission的描述，将permission打印到屏幕或页面时默认显示的就是name
        #
        #                ('can_access_customer_list','可以访问客户列表'),
        #                ('can_access_customer_detail','可以访问客户详细'),
        #                ('can_access_studyrecords','可以访问学习记录页面'),
        #                ('can_access_homework_detail','可以访问作业详情页面'),
        #                ('can_upload_homework','可以交作业'),
        #                ('access_kingadmin_table_obj_detail','可以访问kingadmin每个表的对象'),
        #                ('change_kingadmin_table_obj_detail','可以修改kingadmin每个表的对象'),
        #                )




class ContractTemplate(models.Model):
    '''合同模版'''
    name = models.CharField(verbose_name="合同名称",max_length=64,unique=True)
    template = models.TextField()

    class Meta:
        verbose_name='合同模版'#在Django中显示的别名
    def __str__(self):
        return self.name










