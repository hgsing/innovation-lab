from django import template

register = template.Library()

# template function that's used to get truncated value of an entry in a dictionary
@register.filter
def get_item(dictionary, key):
    if key in dictionary:
        ret = str(dictionary.get(key))
        ret = ret[:30] + '..' * (len(ret) > 30)
        return ret.strip()
    return 'N/A'

@register.filter
def get_full(dictionary, key):
    if key in dictionary:
        return str(dictionary.get(key)).strip()
    return 'N/A'