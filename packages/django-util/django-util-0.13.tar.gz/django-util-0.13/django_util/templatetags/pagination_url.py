from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Create page pagination

    Reference
    ---------
    - https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/
    - https://stackoverflow.com/questions/3324009/how-to-obtain-all-values-of-a-multi-valued-key-from-djangos-request-get-querydi
    - https://stackoverflow.com/questions/46026268/pagination-and-get-parameters
    """
    query = context["request"].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    # print(query)
    # print(query.urlencode())
    return query.urlencode()
