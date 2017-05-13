from django.http.response import Http404, HttpResponseRedirect, HttpResponse, HttpResponseServerError, JsonResponse
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.views import View
from django.shortcuts import render
from elections.forms import CircuitForm
import elections.models


class MainView(View):
    @staticmethod
    def prepare_people(candidates):
        cd = []
        s = 0
        for c in candidates:
            s += c.votes
        for c in candidates:
            c.percentage = round(c.votes * 100 / s, 2)

        for c in candidates:
            cd.append({
                "name": c.__str__(),
                "votes": c.votes,
                "percentage": c.percentage
            })
        return cd


class Country(MainView):
    def get(self, request):
        return JsonResponse({
            "voivodeships": [{"id": v.id, "name": v.name, "code": v.code, "votes": v.votes} for v in
                             elections.models.Voivodeship.objects.annotate(votes=Sum('precinct__boroughs__circuit__candidateresult__votes'))],
            "people": self.prepare_people(elections.models.Candidate.objects.annotate(votes=Sum('candidateresult__votes')).order_by('-votes'))
        })


class Voivodeship(MainView):
    def get(self, request, voivodeship_id):
        v = elections.models.Voivodeship.objects.filter(id=voivodeship_id)
        if not v:
            return JsonResponse({'message': "Voivodeship not found."}, status=404)
        v = v.first()

        data = {
            "name": v.name,
            "people": self.prepare_people(elections.models.Candidate.objects.filter(candidateresult__circuit__borough__precinct__voivodeship_id=v.id).annotate(
                votes=Sum('candidateresult__votes')).order_by('-votes'))
        }

        precincts = elections.models.Precinct.objects.filter(voivodeship_id=v.id)
        data["pages"] = [{'link': 'precinct/' + str(p.id), 'name': p.name + " (" + str(p.id) + ")"} for p in precincts]

        return JsonResponse(data)


class Precinct(MainView):
    def get(self, request, precinct_id):
        precinct = elections.models.Precinct.objects.filter(id=precinct_id)
        if not precinct:
            return JsonResponse({'message': "Precinct not found."}, status=404)
        precinct = precinct.first()

        data = {
            "name": precinct.name,
            "people": self.prepare_people(elections.models.Candidate.objects.filter(candidateresult__circuit__borough__precinct=precinct.id).annotate(
                votes=Sum('candidateresult__votes')).order_by('-votes'))
        }
        boroughs = elections.models.Borough.objects.filter(precinct=precinct.id)
        pages = [{'link': 'borough/' + str(b.id), 'name': b.name} for b in boroughs]
        data["pages"] = pages

        return JsonResponse(data)


class Borough(MainView):
    def get(self, request, borough_id):
        borough = elections.models.Borough.objects.filter(id=borough_id)
        if not borough:
            return JsonResponse({'message': "Borough not found."}, status=404)
        borough = borough.first()

        data = {
            "name": borough.name,
            "borough": True,
            "people": self.prepare_people(elections.models.Candidate.objects.filter(candidateresult__circuit__borough=borough.id).annotate(
                votes=Sum('candidateresult__votes')).order_by('-votes'))
        }

        results = []
        for circuit in elections.models.Circuit.objects.filter(borough=borough.id).order_by("id"):
            candidates = elections.models.Candidate.objects.filter(candidateresult__circuit=circuit.id).annotate(votes=Sum('candidateresult__votes')).order_by(
                'last_name')
            results.append({
                'id': circuit.id,
                'address': circuit.address,
                'votes': [c.votes for c in candidates]
            })
        data["circuits"] = {
            "candidates": [str(c) for c in elections.models.Candidate.objects.order_by("last_name")],
            "results": results
        }

        return JsonResponse(data)


class BoroughSearch(View):
    @staticmethod
    def get(request):
        query = request.GET.get('query')
        if not query:
            return JsonResponse({"message": "Query is not defined."}, status=400)

        results = elections.models.Borough.objects.filter(name__icontains=query)
        data = {
            "searched": True,
            "query": query,
            "results": results
        }
        return JsonResponse(data)


class CircuitEdit(MainView):
    def get(self, request, circuit_id):
        if not request.user.is_authenticated:
            return JsonResponse({'message': "You are not authenticated. Please, log in and try again."}, status=403)
        c = elections.models.Circuit.objects.filter(id=circuit_id)
        if not c:
            return JsonResponse({'message': "Circuit not found."}, status=404)
        circuit = c.first()

        form = CircuitForm(circuit=circuit)
        fields = {}
        for key, value in form.fields.items():
            fields[key] = {
                "label": str(value.label),
                "initial": value.initial,
                "min_value": value.min_value
            }
        data = {
            "name": circuit.address,
            "form": fields
        }

        return JsonResponse(data)

    def post(self, request, circuit_id):
        if not request.user.is_authenticated:
            return JsonResponse({'message': "You are not authenticated. Please, log in and try again."}, status=403)

        try:
            with transaction.atomic():
                circuit = elections.models.Circuit.objects.select_for_update().filter(id=circuit_id)[0]
                form = CircuitForm(request.POST, circuit=circuit)

                if not form.is_valid():
                    return JsonResponse({"message": "Invalid form.", "errors": form.errors}, status=400)

                candidates = []
                valid_votes = 0
                for candidate_id, votes in form.cleaned_data.items():
                    c = elections.models.CandidateResult.objects.get(candidate_id=candidate_id, circuit_id=circuit.id)
                    if not c:
                        return JsonResponse({"message": "Given candidate not found."}, status=404)

                    c.votes = votes
                    candidates.append(c)
                    valid_votes += votes

                circuit.valid_cards = valid_votes
                circuit.save()
                for c in candidates:
                    c.save()

                return JsonResponse(data=None, status=204)

        except IntegrityError:
            return JsonResponse({"message": "Integrity error. Please redo your changes."}, status=500)
