from django.db import models
from django.utils.translation import gettext_lazy as _

TRUE_FALSE_CHOICES = [
    ("", "---"),
    (True, "TRUE"),
    (False, "FALSE"),
]


class PersonBloodChoices(models.TextChoices):
    """
    Person blood enumeration
    """

    DEFAULT = "", _("---")
    A = "A", _("A")
    B = "B", _("B")
    AB = "AB", _("AB")
    O = "O", _("O")
    OTHERS = "OTHERS", _("OTHERS")


class PersonEducationLevelChoices(models.TextChoices):
    """
    Person education level enumeration

    Reference
    ---------
    - https://study.com/different_degrees.html
    """

    DEFAULT = "", _("---")
    HIGH_SCHOOL = "HIGH_SCHOOL", _("HIGH SCHOOL")
    ASSOCIATE = "ASSOCIATE", _("ASSOCIATE DEGREE")
    BACHELOR = "BACHELOR", _("BACHELOR'S DEGREE")
    MASTER = "MASTER", _("MASTER'S DEGREE")
    DOCTORAL = "DOCTORAL", _("DOCTORAL DEGREE")
    OTHERS = "OTHERS", _("OTHERS")


class PersonEyeColorChoices(models.TextChoices):
    """
    Person eye color enumeration

    Reference
    ---------
    - https://en.wikipedia.org/wiki/Eye_color#Eye_color_chart_(Martin_scale)
    """

    DEFAULT = "", _("---")
    AMBER = "AMBER", _("AMBER")
    BLUE = "BLUE", _("BLUE")
    BROWN = "BROWN", _("BROWN")
    GREEN = "GREEN", _("GREEN")
    GREY = "GREY", _("GREY")
    HAZEL = "HAZEL", _("HAZEL")
    RED = "RED", _("RED")
    OTHERS = "OTHERS", _("OTHERS")


class PersonGenderChoices(models.TextChoices):
    """
    Person gender enumeration
    """

    DEFAULT = "", _("---")
    FEMALE = "FEMALE", _("FEMALE")
    MALE = "MALE", _("MALE")
    OTHERS = "OTHERS", _("OTHERS")


class PersonRaceChoices(models.TextChoices):
    """
    Person race enumeration

    Reference
    ---------
    - https://grants.nih.gov/grants/guide/notice-files/not-od-15-089.html
    """

    DEFAULT = "", _("---")
    ASIAN = "ASIAN", _("ASIAN")
    BLACK = "BLACK", _("BLACK OR AFRICAN AMERICAN")
    HISPANIC = "HISPANIC", _("HISPANIC OR LATINO")
    INDIAN = "INDIAN", _("AMERICAN INDIAN OR ALASKA NATIVE")
    ISLANDER = "ISLANDER", _("NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER")
    WHITE = "WHITE", _("WHITE")
    OTHERS = "OTHERS", _("OTHERS")
