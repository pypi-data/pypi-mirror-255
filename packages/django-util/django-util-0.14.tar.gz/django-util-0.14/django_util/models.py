import uuid

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models

from django_util.choices import (
    PersonBloodChoices,
    PersonEyeColorChoices,
    PersonGenderChoices,
    PersonRaceChoices,
)
from django_util.fields import UpperTextField, complex_fields, related_fields


# abstract
class Profile(models.Model):
    """
    Profile model extend Django User model

    Reference
    ---------
    - https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class Base(models.Model):
    """
    The ideal abstract base model

    Reference
    ---------
    - https://docs.djangoproject.com/en/3.0/topics/db/models/#abstract-base-classes
    - https://stackoverflow.com/a/16838663

    Metadata

    - https://dataedo.com/kb/data-glossary/what-is-metadata

    User tracker

    - https://docs.djangoproject.com/en/3.1/topics/class-based-views/generic-editing/#models-and-request-user
    - https://stackoverflow.com/questions/5611410/related-name-argument-not-working-as-expected-in-django-model
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    # The field ConcreteModel.created_by was declared with a lazy reference to 'django_util.profile', but app 'django_util' doesn't provide model 'profile'.
    # The field ConcreteModel.updated_by was declared with a lazy reference to 'django_util.profile', but app 'django_util' doesn't provide model 'profile'.
    # created_by = models.ForeignKey(
    # updated_by = models.ForeignKey(
    #     Profile,
    #     editable=False,
    #     null=True,
    #     on_delete=models.SET_NULL,
    #     related_name="%(class)s_created_by",
    # )
    note = UpperTextField(
        blank=True,
        default="",
    )
    is_admin_verified = models.BooleanField(
        default=False,
        editable=False,
    )

    class Meta:
        abstract = True

    @staticmethod
    def get_base_meta_field_list() -> list:
        return sorted(
            [
                "created_at",
                "updated_at",
            ]
        )

    @staticmethod
    def get_extra_meta_field_list() -> list:
        return sorted(
            [
                # "created_by",
                # "updated_by",
                "note",
                "is_admin_verified",
            ]
        )

    @classmethod
    def get_field_list(cls):
        return sorted([field.name for field in cls._meta.get_fields()])

    @classmethod
    def get_field_list_without_extra_meta(cls):
        return sorted(
            list(set(cls.get_field_list()) - set(cls.get_extra_meta_field_list()))
        )

    @classmethod
    def get_field_list_without_meta(cls):
        return sorted(
            list(
                set(cls.get_field_list())
                - set(cls.get_base_meta_field_list())
                - set(cls.get_extra_meta_field_list())
            )
        )

    @classmethod
    def get_related_field_list(cls):
        field_list = []
        for field in cls._meta.get_fields():
            if isinstance(field, related_fields):
                field_list.append(field.name)
        return sorted(field_list)

    @classmethod
    def get_complex_field_list(cls):
        field_list = []
        for field in cls._meta.get_fields():
            if isinstance(field, complex_fields):
                field_list.append(field.name)
        return sorted(field_list)


class BasePublicContribute(Base):
    """
    Enhanced abstract base model, use if data can be edited by public
    """

    is_verified = models.BooleanField(
        default=False,
    )
    is_hidden = models.BooleanField(
        default=False,
    )

    class Meta:
        abstract = True

    @staticmethod
    def get_staff_only_field_list():
        return sorted(
            [
                "is_hidden",
                "is_verified",
            ]
        )


class EmailHttpRequest(models.Model):
    """
    Abstract model that stores email and HttpRequest fields
    """

    email = models.EmailField(
        db_index=True,
    )
    campaign = UpperTextField(
        blank=True,
        default="",
    )
    http_referrer = UpperTextField(
        blank=True,
        default="",
    )
    http_user_agent = UpperTextField(
        blank=True,
        default="",
    )
    remote_addr = models.GenericIPAddressField(
        blank=True,
        null=True,
    )
    remote_host = UpperTextField(
        blank=True,
        default="",
    )

    class Meta:
        abstract = True


class Person(models.Model):
    """
    Abstract Person model

    Reference
    ---------
    - https://schema.org/Person
    """

    uuid = models.UUIDField(
        db_index=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    english_first_name = UpperTextField(
        default="",
    )
    english_middle_name = UpperTextField(
        blank=True,
        default="",
    )
    english_last_name = UpperTextField(
        default="",
    )
    native_first_name = UpperTextField(
        blank=True,
        default="",
    )
    native_middle_name = UpperTextField(
        blank=True,
        default="",
    )
    native_last_name = UpperTextField(
        blank=True,
        default="",
    )
    alias = ArrayField(
        UpperTextField(),
        blank=True,
        null=True,
    )
    description = UpperTextField(
        blank=True,
        default="",
    )

    # biology
    birth_date = models.DateTimeField(
        blank=True,
        null=True,
    )
    death_date = models.DateTimeField(
        blank=True,
        null=True,
    )
    blood_type = UpperTextField(
        blank=True,
        choices=PersonBloodChoices.choices,
        default=PersonBloodChoices.DEFAULT,
    )
    eye_color = UpperTextField(
        blank=True,
        choices=PersonEyeColorChoices.choices,
        default=PersonEyeColorChoices.DEFAULT,
    )
    gender = UpperTextField(
        blank=True,
        choices=PersonGenderChoices.choices,
        default=PersonGenderChoices.DEFAULT,
    )
    race = UpperTextField(
        blank=True,
        choices=PersonRaceChoices.choices,
        default=PersonRaceChoices.DEFAULT,
    )
    height = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        abstract = True


class FullCalendarEventParseV6(models.Model):
    """
    FullCalendar Event

    Reference
    ---------
    - https://fullcalendar.io/docs/v6/event-parsing
    """

    group_id = models.TextField(
        blank=True,
        default="",
    )
    all_day = models.BooleanField(
        blank=True,
        null=True,
    )
    start = models.DateTimeField(
        blank=True,
        null=True,
    )
    end = models.DateTimeField(
        blank=True,
        null=True,
    )
    days_of_week = ArrayField(
        models.TextField(),
        blank=True,
        null=True,
    )
    start_time = models.TimeField(
        blank=True,
        null=True,
    )
    end_time = models.TimeField(
        blank=True,
        null=True,
    )
    start_recur = models.DateTimeField(
        blank=True,
        null=True,
    )
    end_recur = models.DateTimeField(
        blank=True,
        null=True,
    )
    title = models.TextField(
        blank=True,
        default="",
    )
    url = models.URLField(
        blank=True,
        default="",
    )
    interactive = models.BooleanField(
        blank=True,
        null=True,
    )
    class_name = ArrayField(
        models.TextField(),
        blank=True,
        null=True,
    )
    editable = models.BooleanField(
        blank=True,
        null=True,
    )
    start_editable = models.BooleanField(
        blank=True,
        null=True,
    )
    duration_editable = models.BooleanField(
        blank=True,
        null=True,
    )
    resource_editable = models.BooleanField(
        blank=True,
        null=True,
    )
    resource_id = models.TextField(
        blank=True,
        default="",
    )
    resource_ids = ArrayField(
        models.TextField(),
        blank=True,
        null=True,
    )
    display = models.TextField(
        blank=True,
        default="",
    )
    overlap = models.BooleanField(
        blank=True,
        null=True,
    )
    constraint = models.BooleanField(
        blank=True,
        null=True,
    )
    color = models.BooleanField(
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True
