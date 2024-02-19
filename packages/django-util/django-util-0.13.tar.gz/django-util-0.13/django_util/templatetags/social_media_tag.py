from django import template

register = template.Library()


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
