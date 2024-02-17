from django.db import models
from . import choices

# Create your models here.

class Address(models.Model):
    """A Person's Address"""

    area = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=2, choices=choices.LOCATION_COUNTRIES)
    state = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    # Municipal, Local Government Area
    lga = models.CharField(max_length=255, blank=True, null=True)
    # Private Mail Box/ Post Office Box
    pmb = models.CharField(max_length=255, blank=True, null=True)
    typefk = models.IntegerField(default=1, choices=choices.LOCATION_TYPES)
    village = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        """Meta class for this Model"""

        abstract = True
        managed = True


class Email(models.Model):
    """A Person's Email Address"""

    email = models.CharField(max_length=255, blank=True, null=True)
    typefk = models.IntegerField(default=1, choices=choices.LOCATION_TYPES)

    class Meta:
        """Meta class for this Model"""

        abstract = True
        managed = True


class Event(models.Model):
    """An event in a Person's Life"""

    authority = models.CharField(max_length=255)
    end_date = models.DateTimeField(blank=True, null=True)
    internalfk = models.CharField(max_length=255, blank=True, null=True)
    proof = models.IntegerField(
        blank=True, choices=choices.EVENT_PROOFS, null=True
    )
    reference = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    typefk = models.IntegerField(choices=choices.EVENT_TYPES)

    class Meta:
        """Meta class for this Model"""

        abstract = True
        managed = True


class Group(models.Model):
    """Model of a Group of Persons"""

    about = models.CharField(blank=True, max_length=255, null=True)
    motto = models.CharField(blank=True, max_length=255, null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        """Print String for this Model"""

        return self.name

    class Meta:
        """Meta class for this Model"""

        abstract = True
        managed = True


class Organization(models.Model):
    """A model of An Organization"""

    name = models.CharField(max_length=255)
    services = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=255)
    motto = models.CharField(max_length=255)

    def __str__(self):
        """A text for identifying the Organization"""

        return self.name

    class Meta:
        """Meta class for Organization"""

        abstract = True
        managed = True


class Person(models.Model):
    """Model of a Person/Human"""

    blood_group = models.IntegerField(
        blank=True, choices=choices.BLOODGROUP, null=True
    )
    first_name = models.CharField(max_length=255)
    genotype = models.IntegerField(
        blank=True, choices=choices.GENOTYPE, null=True
    )
    last_name = models.CharField(max_length=255)
    marital_status = models.IntegerField(
        blank=True, choices=choices.MARITALSTATUS, null=True
    )
    middle_name = models.CharField(blank=True, max_length=255, null=True)
    nationality = models.CharField(
        default="NG", max_length=2, choices=choices.LOCATION_COUNTRIES
    )
    nickname = models.CharField(blank=True, max_length=255, null=True)
    prefix = models.CharField(blank=True, choices=choices.HONORIFIC, null=True)
    religion = models.CharField(choices=choices.RELIGION)
    sex = models.IntegerField(choices=choices.SEX)
    suffix = models.CharField(blank=True, choices=choices.HONORIFIC, null=True)

    def __str__(self):
        """Print String for this Model"""

        return self.last_name

    def full_name(self): 
        """Return the fullname of this Person""" 
 
        return f"{self.prefix} {self.last_name}, {self.first_name} {self.middle_name}" 

    class Meta:
        """Meta class for this Model"""

        abstract = True
        managed = True


class Phone(models.Model):
    """A Person's Phone Number"""

    number = models.CharField(max_length=255, blank=True, null=True)
    typefk = models.IntegerField(default=4, choices=choices.LOCATION_TYPES)

    class Meta:
        """Meta class for this Model"""

        abstract = True
        managed = True



