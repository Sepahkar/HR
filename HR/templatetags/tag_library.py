from django import template

register = template.Library()

@register.filter()
def zarb(num1,num2):
    return int(num1)*int(num2)

@register.filter(name='get_dic_key')
def get_dic_key(d, key):
    return d.get(key, '')



@register.filter()
def to_money(value):
    return '{:,}'.format(value).split(".")[0]


@register.filter(name="get_dict")
def get_dict(_d,key):
    if _d:
        if key in _d.keys():
            return _d.get(key)
    return ''


@register.filter(name="get_team_corp_value")
def get_team_corp_value(_l,keys):
    ret = ''
    try:
        if _l and len(keys.split(',')) == 2:

            arr = keys.split(',')
            team_name = arr[0]
            corp_name = arr[1]

            for item in _l:
                if item.get('corp') == corp_name and item.get('team') == team_name:
                    ret = item.get('weight')
                    ret = float(ret * 100)
                    ret = "{:.2f}".format(ret)
                    break
    except:
        ret = 0
    return ret

@register.filter(name="concat_str")
def concat_str(val1,val2):
    return val1 + ',' + val2




