
'''进行条件过滤并返回过滤后的数据,返回的第一个只是queryset类型的,第二个是字典类型'''
from django.db.models import Q

'''返回过滤后的内容'''
def table_filter(request,admin_class):
    filter_conditions = {}
    keywords = ['page','_q','o']
    # print('rrrrrrr',request.GET)
    #<QueryDict: {'source': ['1'], 'consultant': [''], 'consult_course': [''], 'status': [''], 'date__gte': [''], '_q': ['']}>

    for k,v in request.GET.items():
        if k in keywords:#保留的分页关键字 and 排序关键字
            continue
        if v:
            filter_conditions[k] = v

    print('filter_conditions',filter_conditions)
    return admin_class.model.objects.filter(**filter_conditions),filter_conditions

'''返回搜索后的结果'''
def table_search(request,admin_class,object_list):
    search_key = request.GET.get("_q","")#搜索的内容,注意是get请求！！！！
    q_obj = Q()
    q_obj.connector = "OR"
    for column in admin_class.search_fields:
        q_obj.children.append(("%s__contains"%column, search_key))
        #    q1.children.append(('id', 1))
        #    q1.children.append(('id', 10))
    result = object_list.filter(q_obj)#queryset 可以继续通过.filter来筛选值
    print("result",result)
    return result

'''返回排序后的结果'''
def table_sort(request,admin_class,object_list):
    '''排序功能，需要排序的字段，正序、反序'''
    orderby_key = request.GET.get("o")#排序的字段
    if orderby_key:#有需要排序的字段
        res = object_list.order_by(orderby_key)#先取得排序的结果

        if orderby_key.startswith("-"):
            orderby_key = orderby_key.strip("-")
        else:
            orderby_key = "-%s"%orderby_key#否则加上负号，即将相反的字段返回给前端，
            # 下一次再点击排序的时候，发送过来的字段的正负就是正确的
    else:
        res = object_list

    return res,orderby_key


