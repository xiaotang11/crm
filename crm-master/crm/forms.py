from django.forms import ModelForm
from crm import models

#注册的表单
class EnrollmentForm(ModelForm):

    def __new__(cls, *args, **kwargs):
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
        return ModelForm.__new__(cls)
    class Meta:
        model =  models.Enrollment
        fields = ["enrolled_class","consultant"]#用户信息不能放在ModelForm表单里面，应该单独直接加在页面上，因为该信息不能修改

 #填写报名信息的页面表单
class CustomerForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name,field_obj in cls.base_fields.items():#base_fields指代的就是每一个fields，可以去源码看
            field_obj.widget.attrs['class'] = 'form-control'#给每个字段加样式

            if field_name in cls.Meta.readonly_fields:#给只读字段加个前端样式
                field_obj.widget.attrs['disabled'] = 'disabled'

        return ModelForm.__new__(cls)

    def clean_qq(self):
        if self.instance.qq != self.cleaned_data['qq']:
            self.add_error("qq","qq号不能修改")
        return self.cleaned_data['qq']

    def clean_consultant(self):
        if self.instance.consultant != self.cleaned_data['consultant']:
            self.add_error("consultant","咨询顾问不能修改")
        return self.cleaned_data['consultant']

    class Meta:
        model = models.Customer
        fields = "__all__"
        exclude = ['tags','content','memo','status','referral_from','consult_course']

        readonly_fields = [ 'qq','consultant','source']#在__new__对readonly_fields做处理，给其加上样式
