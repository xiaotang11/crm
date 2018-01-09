#自定义标签
from django.core.exceptions import FieldDoesNotExist
from django.utils.timezone import datetime,timedelta
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

#返回显示表名
@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name

'''返回可以排序的table头'''
@register.simple_tag
def build_table_header_column(column,orderby_key,filter_condtions,admin_class):
    #<th><a href="?{filters}&o={orderby_key}">{column}</a> {sort_icon} </th>
    filters = ''
    for k,v in filter_condtions.items():#过滤字段有哪些，要在过滤的基础后上排序
        filters +="&%s=%s"%(k,v)

    ele = '''<th><a href="?{filters}&o={orderby_key}">{column}</a> {sort_icon} </th>'''
    if orderby_key:
        if orderby_key.startswith("-"):#加小箭头
            sort_icon = '''<span class="glyphicon glyphicon-arrow-up"></span>'''
        else:
            sort_icon = '''<span class="glyphicon glyphicon-arrow-down"></span>'''
        if orderby_key.strip("-") == column:#显示的这个字段刚好就是排序的哪个字段
            orderby_key = orderby_key
        else:#不需要排序，就构造当前的a标签，以便下次排序
            orderby_key =column
            sort_icon = ""

    else:#没有排序，就构造当前的a标签，以便下次排序
        orderby_key = column
        sort_icon = ''
    try:#获取每个字段的别名来作为表头
        column_verbose_name = admin_class.model._meta.get_field(column).verbose_name
    except FieldDoesNotExist:#如果表里面没有这个字段，则看一下这个字段是不是自定义的连接字段
        column_verbose_name = getattr(admin_class,column).display_name
        ele = '''<th><a href="javascript:void(0);">{column}</a></th>'''.format(column = column_verbose_name)
        return mark_safe(ele)
    ele = ele.format(filters=filters,orderby_key=orderby_key,column=column_verbose_name,sort_icon=sort_icon)
    return mark_safe(ele)

#返回过滤字段下拉框的内容，即构造过滤字段里面的子标签select  option选项
@register.simple_tag
def render_filter_ele(filter_field,admin_class,filter_condtions):
    #select_ele = '''<select class="form-control" name='%s' ><option value=''>----</option>''' %filter_field
    select_ele = '''<select class="form-control" name='{filter_field}' ><option value=''>----</option>'''
    field_obj = admin_class.model._meta.get_field(filter_field)
    if field_obj.choices:
        selected =""
        for choice_item in field_obj.choices:
            # print("choice",choice_item,filter_condtions.get(filter_field),type(filter_condtions.get(filter_field)))
            # print('choice_item[0]', choice_item[0])
            '''
            choice (0, '已报名') None <class 'NoneType'>
            choice_item[0] 0
            choice (1, '未报名') None <class 'NoneType'>
            choice_item[0] 1
            '''
            if filter_condtions.get(filter_field) ==str(choice_item[0]):
                selected = "selected"
                # 默认第一行被选中
            select_ele +='''<option value='%s' %s>%s</option>'''%(choice_item[0],selected,choice_item[1])
            selected = ""

    if type(field_obj).__name__ == "ForeignKey":
        selected=""
        for choice_item in field_obj.get_choices()[1:]:
            if filter_condtions.get(field_obj) == str(choice_item[0]):
                #choice_item[0] s是0
                selected = "selected"
            select_ele +='''<option value='%s' %s>%s</option>'''%(choice_item[0],selected,choice_item[1])
            selected=""

    if type(field_obj).__name__ in ['DateTimeField', 'DateField']:
        '''将date_els 构造成 [
            ['今天', datetime.now().date()],
            ["昨天",today_ele - timedelta(days=1)],
            ["近7天",today_ele - timedelta(days=7)],
         ]'''
        date_els = []
        today_ele = datetime.now().date()
        date_els.append(['今天',today_ele])
        date_els.append(['昨天', today_ele - timedelta(days=1)])
        date_els.append(["近7天",today_ele - timedelta(days=7)])
        date_els.append(["近30天",today_ele - timedelta(days=30)])

        date_els.append(["本月1号",today_ele.replace(day=1)])
        date_els.append(["本年",today_ele.replace(month=1,day=1)])

        selected=""
        for item in date_els:
            select_ele +='''<option value='%s' %s>%s</option>'''%(item[1],selected,item[0])
        filter_field_name = "%s__gte"%filter_field #为日期类型时，要将date 改为date__gte，即日期范围是从选中的日期起
    else:
        filter_field_name = filter_field
    select_ele +="</select>"
    select_ele = select_ele.format(filter_field=filter_field_name)

    return mark_safe(select_ele)

#返回表查询内容，querysets类型
@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()

#返回表对应显示的内容
@register.simple_tag
def build_table_row(request,obj,admin_class):
    '''构造表的内容，在表上将list_display里面要显示的字段名和内容相应的对应上，显示出来
        request用于传request.path来构造路径'''
    row_ele =""
    for index,column in enumerate(admin_class.list_display):
        try:#如果该字段不是数据库里面的字段，则接收一下错误，看一下有没有这个方法
            field_obj = obj._meta.get_field(column)
            if field_obj.choices:#这个字段的choices不为空，则为choices type
                column_data = getattr(obj, "get_%s_display"%column)()
            else:
                column_data = getattr(obj,column)
                # 即将obj.'title'变成 obj.title，然后返回到前端

            if type(column_data).__name__=='datetime':
                column_data = column_data.strftime("%Y-%m-%d %H:%M:%S")
                # 将时间的显示方式处理一下
            if index ==0:#可以跳转到修改页面  (index为0对应的是id 列，即让id字段为a标签，可以跳转到修改页面)
                column_data = "<a href='{request_path}{obj_id}/change/'>{data}</a>".format(request_path = request.path,
                                                                                           obj_id = obj.id,
                                                                                           data = column_data)
        except FieldDoesNotExist:
            if hasattr(admin_class,column):#如果admin_class里面有这个字段函数，就获取它的返回值
                column_func = getattr(admin_class,column)
                admin_class.instance = obj #同时将当前对象和请求传给admin class，以便函数调用时使用id和当前路径
                admin_class.request = request
                column_data = column_func()#enroll（）

        row_ele += "<td>%s</td>" % column_data
    return mark_safe(row_ele)

# @register.simple_tag
# def render_page_ele(loop_counter,query_sets):
#     #循环总数，查询条件
#     if abs(query_sets.number - loop_counter)<=1:
#         ele_class =""
#         if query_sets.number == loop_counter:
#             ele_class = "active"
#         ele = '''<li class="%s"><a href="?page=%s">%s</a></li>'''%(ele_class,loop_counter,loop_counter)
#         return mark_safe(ele)

#返回表别名
@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.verbose_name

#返回分页按钮
@register.simple_tag
def build_paginators(query_sets,filter_condtions,search_text,orderby_key):
    page_btns = ''
    filters = ""
    for k,v in filter_condtions.items():#如果有过滤的字段，将过滤的字段加到a标签里面
        filters = "&%s=%s"%(k,v)

    for page_num in query_sets.paginator.page_range:
        ele_class=""
        if query_sets.number == page_num:
            ele_class = "active"
        print('query_sets.paginator.page_range',query_sets.paginator)
#构造页码按钮

        page_btns +='''<li class="%s"><a href="?page=%s%s&_q=%s&o=%s">%s</a></li>'''%(
            ele_class,page_num,filters,search_text,orderby_key,page_num
        )

    return mark_safe(page_btns)



@register.simple_tag
def get_action_verbose_name(admin_class,action):
    action_func= getattr(admin_class,action)

    return  action_func.display_name if hasattr(action_func,'display_name') else action

@register.simple_tag
def display_obj_related(objs):
    '''把对象及所有相关联的数据取出来'''
    # 这是为批量删除设计出来的功能
    print('objs',objs)
    #objs [<Customer: <44 爱狗狗>>]
    if objs:#objs 必须是queryset类型的
        return mark_safe(recursive_related_objs_lookup(objs))

def recursive_related_objs_lookup(objs):
    ul_ele = "<ul>"
    for obj in objs:  # objs 必须是queryset类型的，才能for循环
        print('obj', obj)
        '''obj <44 爱狗狗>'''
        li_ele = '''<li> %s: %s </li>''' % (obj._meta.verbose_name, obj.__str__().strip("<>"))
        # 显示   表名：对象名字
        ul_ele += li_ele

        # print("------- obj._meta.local_many_to_many", obj._meta.local_many_to_many)
        for m2m_field in obj._meta.local_many_to_many:  # 把所有跟这个对象直接关联的m2m字段取出来了
            sub_ul_ele = "<ul>"
            m2m_field_obj = getattr(obj, m2m_field.name)  # getattr(customer, 'tags')
            for o in m2m_field_obj.select_related():  # customer.tags.select_related()
                li_ele = '''<li> %s: %s </li>''' % (m2m_field.verbose_name, o.__str__().strip("<>"))
                sub_ul_ele += li_ele

            sub_ul_ele += "</ul>"
            ul_ele += sub_ul_ele  # 最终跟最外层的ul相拼接

        for related_obj in obj._meta.related_objects:
            # obj._meta.related_objects来取到和他有关联关系的对象 ManyToManyRel ，多对多的除外
            if 'ManyToManyRel' in related_obj.__repr__():  # ManyToManyRel时，不让其递归
                # related_obj.__repr__()返回的是他的字符串格式
                if hasattr(obj, related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                    accessor_obj = getattr(obj,
                                           related_obj.get_accessor_name())  # accessor_obj = customer.enrollment_set
                    print("-------ManyToManyRel", accessor_obj, related_obj.get_accessor_name())
                    # 上面accessor_obj 相当于 customer.enrollment_set
                    if hasattr(accessor_obj, 'select_related'):  # select_related() 和all()的效果是一样的
                        target_objs = accessor_obj.select_related()  # .filter(**filter_coditions)
                        # target_objs 相当于 customer.enrollment_set.all()

                        sub_ul_ele = "<ul style='color:red'>"
                        for o in target_objs:
                            li_ele = '''<li> %s: %s </li>''' % (o._meta.verbose_name, o.__str__().strip("<>"))
                            sub_ul_ele += li_ele
                        sub_ul_ele += "</ul>"
                        ul_ele += sub_ul_ele

            elif hasattr(obj,
                         related_obj.get_accessor_name()):  # ManyTooneRel时，让其递归  # hassattr(customer,'enrollment_set')
                accessor_obj = getattr(obj, related_obj.get_accessor_name())
                # 上面accessor_obj 相当于 customer.enrollment_set
                if hasattr(accessor_obj, 'select_related'):  # slect_related() == all()
                    target_objs = accessor_obj.select_related()  # .filter(**filter_coditions)
                    # target_objs 相当于 customer.enrollment_set.all()
                else:
                    print("one to one i guess:", accessor_obj)
                    target_objs = accessor_obj

                # 这个地方的递归有点问题，暂时将其驻掉，否则某些情况可能会陷入递归的死循环！！！
                # if len(target_objs) > 0:
                #     # 递归循环，将内层的关系也找出来显示
                #     # print("\033[31;1mdeeper layer lookup -------\033[0m")
                #     # nodes = recursive_related_objs_lookup(target_objs,model_name)
                #     nodes = recursive_related_objs_lookup(target_objs)
                #     ul_ele += nodes
    ul_ele += "</ul>"
    return ul_ele




