from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Address(TimestampedModel):
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
        db_table = "address"
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        abstract = False


class Contact(TimestampedModel):
    email = models.EmailField(blank=True, unique=True)
    phone = models.CharField(max_length=11, blank=True)

    def __str__(self):
        return f"{self.email} / {self.phone}"

    class Meta(TimestampedModel.Meta):
        db_table = "contact"
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        abstract = False


class DomType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
