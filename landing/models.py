from django.db import models
from django.utils import timezone


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created = models.DateTimeField(default=timezone.now, db_index=True)
    is_read = models.BooleanField("Read", default=False)
    notes = models.TextField("Internal notes", blank=True)

    DisplayFields = ['name', 'email', 'subject', 'message']
    SearchableFields = ['name', 'email']
    FilterFields = ['name', 'email']

    class Meta:
        ordering = ["-created"]
        verbose_name = "message"

    def __str__(self):
        return self.name
