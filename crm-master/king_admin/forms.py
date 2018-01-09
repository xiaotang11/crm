from django.core.exceptions import ValidationError
from django.forms import ModelForm, models

# 传统创建modelform的方法
# class CustomerModelForm(ModelForm):
#     class Meta:
#         model = models.Customer
#         fields = "__all__"

def create_model_form(request,admin_class):
    '''动态生成不同表单的MODEL FORM类'''
    # class Meta:
    #     model = admin_class.model
    #     fields = "__all__"
    # attrs = {'Meta':Meta}
    # _model_form_class =  type("DynamicModelForm",(ModelForm,),attrs)
    # #通过type类来动态创建modelform类，该类继承ModelForm
    # return _model_form_class
    # model_form怎么加前端的样式呢？通过__new__方法来加
    def __new__(cls,*args,**kwargs):
        #__new__实在__init__之前执行的，将其用来给前端增加样式！！！cls是调用该类是传进来的参数
        # super(CustomerForm, self).__new__(*args, **kwargs)
        # print("base_fields",cls.base_fields)
        for field_name,field_obj in cls.base_fields.items():
            # print(field_name,dir(field_obj))
            field_obj.widget.attrs['class']='form-control'#widget用与给前端加属性

            if not hasattr(admin_class,"is_add_form"): #代表这是修改页面
            # is_add_form这个属性用来判断是add页面还是change页面，add页面就不加disabled属性了
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs['disabled'] = 'disabled'
                #将只读的字段设为disabled，但是disabled的字段提交不了，所以可以再提交前通过js语句将其disabled属性去掉，这样就可以提交过去了
        return ModelForm.__new__(cls)

    def default_clean(self):
        '''给所有的form默认加一个clean验证，验证只读的字段，前端提交过来的值，和后端本来的值是否相等'''
        print("---running default clean",admin_class)
        print("---running default clean",admin_class.readonly_fields)
        print("---obj instance",self.instance)#self.instance是数据库里的本来的值
        print("---self.cleaned_data",self.cleaned_data)#self.cleaned_data是从前端拿到的值

        error_list = []
        if self.instance.id:  # 说明这是个修改的表单，添加是没有instance对象的
            for field in admin_class.readonly_fields:
                field_val = getattr(self.instance, field)  # 从数据库里拿到的每个字段本来的值
                field_val_from_frontend = self.cleaned_data.get(field)  # 从前端拿到的每个字段的值

                print("--前后端值进行比较:", field, field_val, field_val_from_frontend)
                if field_val != field_val_from_frontend:
                    # 如果前端返回的值和后端拿到得值不相等，即只读字段被修改过了，报错
                    error_list.append(ValidationError(
                        ('字段 %(field)s 是只读字段，值应该是 %(val)s'),
                        code='invalid',
                        params={'field': field, 'val': field_val},
                    ))

    # 扩展，进行用户自定制的验证，同时将返回的错误信息添加到error_list 中

        #如果是只读的表单，直接抛错
        if admin_class.readonly_table:
            raise ValidationError(
                                ('Table is  readonly,cannot be modified or added'),
                                code='invalid'
                           )
        self.ValidationError = ValidationError
        # 扩展，进行用户自定制的验证
        response = admin_class.default_form_validation(self)
        if response:
            error_list.append(response)

        if error_list:  # 将多个错误都添加到error_list，一起展示
            raise ValidationError(error_list)

    class Meta:
        model = admin_class.model #表名
        fields = "__all__"
        exclude = admin_class.modelform_exclude_fields#修改页面不显示哪些字段
    attrs = {'Meta':Meta}
    _model_form_class =  type("DynamicModelForm",(ModelForm,),attrs)
    #用type类来动态创建类，该类继承ModelForm基类,将函数名封装到字典中穿给attrs,从此该类中就有该函数
    setattr(_model_form_class,"__new__",__new__)
    #给这个类增加属性，可以通过_model_form_class.__new__来调用,__new__方法比__init__方法还要先执行
    setattr(_model_form_class,'clean',default_clean)
    #将只读字段的验证功能加进去

    print("model form",_model_form_class.Meta.model )
    return _model_form_class















