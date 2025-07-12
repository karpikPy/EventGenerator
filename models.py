from django.db import models
from django.db.models import ForeignKey
from django.db.models.fields import CharField


class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=50)

class Event (models.Model):
    organizer = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Invitation(models.Model):
    class Status(models.TextChoices):
        invited = 'IN', 'запрошено'
        submitted = 'SUB', 'підтверджено'
        declined = 'DEC', 'відхилено'

    event = ForeignKey(Event, related_name='invitations', on_delete=models.CASCADE)
    guest = ForeignKey(User, on_delete=models.CASCADE)
    status = CharField(max_length=2, choices=Status.choices, default=Status.invited)
    sent_at = models.DateTimeField(auto_now_add=True)
