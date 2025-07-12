from django import forms
from .models import Invitation, Event


class EventForm(forms.Form):
    class Meta:
        model = Event

        fields = [
            'organizer',
            'title',
            'description',
            'start_time',
            'end_time'
        ]

class InvitationForm(forms.Form):
    class Meta:
        model = Invitation

        base_fields = [
            'event',
            'guest',
            'status'
        ]