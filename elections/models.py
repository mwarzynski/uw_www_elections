from django.db import models
from django.core.exceptions import ValidationError


class Circuit(models.Model):
    address = models.CharField(max_length=250, unique=True)
    borough = models.ForeignKey('Borough', on_delete=models.CASCADE)
    cards = models.IntegerField()
    valid_cards = models.IntegerField()

    def __str__(self):
        return self.address

    def clean(self):
        if self.cards < 0:
            raise ValidationError("Number of given cards cannot be negative.")
        if self.valid_cards > self.cards:
            raise ValidationError("Circuit cannot have more valid cards than all cards.")


class Borough(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class Precinct(models.Model):
    name = models.CharField(max_length=250)
    number = models.IntegerField(unique=True)
    voivodeship = models.ForeignKey('Voivodeship', on_delete=models.CASCADE)
    boroughs = models.ManyToManyField(Borough)


class Voivodeship(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    def __str__(self):
        return self.first_name + " " + self.last_name

    class Meta:
        unique_together = ('first_name', 'last_name')


class CandidateResult(models.Model):
    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    votes = models.IntegerField()

    def __str__(self):
        return str(self.circuit) + ": " + str(self.candidate)

    class Meta:
        unique_together = ('circuit', 'candidate')
