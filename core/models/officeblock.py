from django.db import models
from rest_framework.exceptions import ValidationError


class OfficeBlock(models.Model):
    name = models.CharField(max_length=50,
                            blank=False, null=False, unique=True)

    def clean(self):
        self.name = " ".join(self.name.title().split())

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except Exception as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Office Block"

    def __str__(self):
        return self.name


class OfficeFloor(models.Model):
    number = models.PositiveIntegerField(blank=False, null=False)
    block = models.ForeignKey(OfficeBlock, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('block', 'number'),)
        verbose_name = 'Office Floor'
        ordering = ['-id']

    def __str__(self):
        return "{}".format(self.number)


class OfficeFloorSection(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    floor = models.ForeignKey(OfficeFloor, on_delete=models.PROTECT)

    def clean(self):
        self.name = " ".join(self.name.title().split())

    def save(self, *args, **kwargs):
        """
        Validate office floor section name
        """
        try:
            self.full_clean()
        except Exception as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (('floor', 'name'),)
        verbose_name = 'Office Floor Section'
        ordering = ['-id']

    def __str__(self):
        return self.name
