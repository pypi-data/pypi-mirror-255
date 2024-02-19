from django import template
from django.templatetags.static import static
from django.urls import reverse

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


@register.filter
def as_abs_url(path, request):
    """
    Build Absolute url

    Reference
    ---------
    - https://stackoverflow.com/questions/19024159/how-to-reverse-a-name-to-a-absolute-url-in-django-template/34630561
    """
    return request.build_absolute_uri(path)


@register.filter
def get_image_url(queryset, i):
    """
    Get image queryset specific index

    Reference
    ---------
    - https://stackoverflow.com/questions/4651172/reference-list-item-by-index-within-django-template
    - https://stackoverflow.com/questions/28286207/reference-static-files-in-django-in-py-files-not-in-templates
    """
    try:
        return queryset[int(i)].image.url
    except IndexError:
        return static("img/no_image_available.svg")
    else:
        return


@register.filter
def social_media_name_mapper(str_):
    hashmap = {
        "crunchbase": "crunchbase",
        "facebook": "facebook",
        "instagram": "instagram",
        "linkedin": "linkedin",
        "tiktok": "tiktok",
        "twitter": "twitter",
        "wikipedia": "wikipedia",
        "youtube": "youtube",
    }
    return hashmap.get(str_, None)


# tags
@register.simple_tag
def combine_url_lists(list1, list2):
    """
    Combine two provided lists
    """
    return list1 + list2


@register.simple_tag(takes_context=True)
def abs_url(context, view_name, *args, **kwargs):
    """
    Build absolute url

    Reference
    ---------
    - https://stackoverflow.com/questions/19024159/how-to-reverse-a-name-to-a-absolute-url-in-django-template/34630561
    """
    # Could add except for KeyError, if rendering the template
    # without a request available.
    return context["request"].build_absolute_uri(
        reverse(
            view_name,
            args=args,
            kwargs=kwargs,
        )
    )


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
