from django.db import models


class Circuit(models.Model):
    address = models.CharField(max_length=250)
    borough = models.ForeignKey('Borough', on_delete=models.CASCADE)
    cards = models.IntegerField()
    valid_cards = models.IntegerField()


class Borough(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField()


class Precinct(models.Model):
    name = models.CharField(max_length=250)
    number = models.IntegerField(unique=True)
    voivodeship = models.ForeignKey('Voivodeship', on_delete=models.CASCADE)
    boroughs = models.ManyToManyField(Borough)


class Voivodeship(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)


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
