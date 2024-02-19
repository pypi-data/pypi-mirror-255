from django import template
from django.templatetags.static import static

register = template.Library()


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
