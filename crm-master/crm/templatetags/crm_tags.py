from django import template


register = template.Library()
@register.simple_tag
def render_enroll_contract(enroll_obj):

    # return enroll_obj.enrolled_class.contract.template.\
    #     format(course_name=enroll_obj.enrolled_class, stu_name=enroll_obj.customer.qq)
    #合同中有些变量需要替换的用.format
    try:
        contract = enroll_obj.enrolled_class.contract.template
    except AttributeError:
        contract = "数据库中没有合同，请添加，并在班级表中绑定合同"
    return contract
