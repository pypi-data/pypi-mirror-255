from django import template
from django.urls import reverse

register = template.Library()


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


@register.filter
def as_abs_url(path, request):
    """
    Build Absolute url

    Reference
    ---------
    - https://stackoverflow.com/questions/19024159/how-to-reverse-a-name-to-a-absolute-url-in-django-template/34630561
    """
    return request.build_absolute_uri(path)
