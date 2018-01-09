#__author:  Administrator


#url type : 0 = related , 1 absolute

perm_dic = {#这个key和models中meta里面定义的权限是一样的
     'crm.can_access_my_course': {
         'url_type':0,
         'url': 'stu_my_classes', #url name  相对地址
         'method': 'GET',
         'args': []
     },
    'crm.can_access_customer_list':{
        'url_type':1,
        'url': '/king_admin/crm/customer/',  # url name 绝对地址
        'method': 'GET',
        'args': []
    },
    '__crm.can_access_customer_detail':{
        'url_type':0,
        'url': 'table_obj_change',  # url name
        'method': 'GET',
        'args': []
    },
    'crm.can_access_studyrecords': {
        'url_type': 0,
        'url': 'studyrecords',  # url name
        'method': 'GET',
        'args': []
    },
    'crm.can_access_homework_detail': {
        'url_type': 0,
        'url': 'homework_detail',  # url name
        'method': 'GET',
        'args': []
    },
    'crm.can_upload_homework': {
        'url_type': 0,
        'url': 'homework_detail',  # url name
        'method': 'POST',
        'args': []
    },
    'crm.access_kingadmin_table_obj_detail': {
        'url_type': 0,
        'url': 'table_obj_change',  # url name
        'method': 'GET',
        'args': []
    },
    'crm.change_kingadmin_table_obj_detail': {
        'url_type': 0,
        'url': 'table_obj_change',  # url name
        'method': 'POST',
        'args': [],
        'hooks':['func1' and  'func2']

    },
}