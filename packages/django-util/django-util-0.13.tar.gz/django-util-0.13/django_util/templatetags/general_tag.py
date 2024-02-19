from django import template

register = template.Library()


# filter
@register.filter
def get_item(dictionary, key):
    """
    Get dictionary value based on key
    """
    return dictionary.get(key)


@register.filter
def index(indexable, i):
    """
    Get index value of indexable
    """
    return indexable[i]


@register.filter
def sentence_case(str_):
    """
    Convert to sentence case
    """
    if str_:
        return ". ".join([l.capitalize() for l in str_.split(". ")])
    else:
        return


@register.filter
def list_to_newline(list_):
    """
    Convert list into string with newline
    """
    if isinstance(list_, list) and list_:
        return "\n".join(list_)
    else:
        return "---"


@register.filter
def ifinlist(value, list_):
    """
    Check if value is in list
    """
    return value in list_


# simple tag
@register.simple_tag
def combine_url_lists(list1, list2):
    """
    Combine two provided lists
    """
    return list1 + list2
