"""
Models for the shared app in Django.
This module contains common models used across the application.
"""

from django.db import models


class TimestampedModel(models.Model):
    """
    Abstract model that adds created_at and updated_at fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for the TimestampedModel.
        """

        abstract = True


class Address(TimestampedModel):
    """
    Model representing an address.
    """

    street = models.CharField(max_length=255)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=100)
    neighbourhood = models.CharField(max_length=150, blank=True)
    number = models.IntegerField()
    postal_code = models.CharField(max_length=8)
    complement = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.street}, {self.city}/{self.state} - {self.postal_code}"

    class Meta(TimestampedModel.Meta):
        """
        Meta options for the Address model.
        """

        db_table = "address"
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        abstract = False


class Contact(TimestampedModel):
    """
    Model representing a contact.
    """

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=11, blank=True)

    def __str__(self):
        return f"{self.email} / {self.phone}"

    class Meta(TimestampedModel.Meta):
        """
        Meta options for the Contact model.
        """

        db_table = "contact"
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        abstract = False


class DomType(models.Model):
    """
    Model representing a domain type.
    """

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        """
        Meta options for the DomType model.
        """

        abstract = True
