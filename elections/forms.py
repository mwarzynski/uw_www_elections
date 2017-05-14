from django import forms
from django.core.exceptions import ValidationError


class CircuitForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.circuit = kwargs.pop('circuit')
        super(CircuitForm, self).__init__(*args, **kwargs)


    def clean(self):
        total_votes = self.circuit.cards

        votes = 0
        for field, candidate_votes in self.cleaned_data.items():
            votes += candidate_votes
            if votes < 0:
                raise ValidationError("Kandydat nie może dostać ujemnych głosów.")

        if votes > total_votes:
            raise ValidationError("Zbyt wiele ważnych głosów dla obwodu.")
