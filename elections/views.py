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

    @staticmethod
    def get_circuit(circuit_id):
        try:
            return elections.models.Circuit.objects.get(id=circuit_id)
        except elections.models.CandidateResult.DoesNotExist:
            raise Http404("Given circuit not found.")


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
            return JsonResponse({'status': 'false', 'message': "Voivodeship not found."}, status=404)
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
            return JsonResponse({'status': 'false', 'message': "Precinct not found."}, status=404)
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
            return JsonResponse({'status': 'false', 'message': "Borough not found."}, status=404)
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
        data = {
            'title': 'Wyszukiwarka gmin.',
            'searched': False,
        }
        query = request.GET.get('query')
        if not query:
            return render(request, "manage/search.html", context=data)

        results = elections.models.Borough.objects.filter(name__icontains=query)
        data['searched'] = True
        data['query'] = query
        data['results'] = results

        return render(request, "manage/search.html", context=data)


class CircuitEdit(MainView):
    def generate_data(self, circuit_id):
        circuit = self.get_circuit(circuit_id)
        return {
            "title": "Edycja obwodu - " + str(circuit.address) + " (" + str(circuit.id) + ")",
            "circuit": circuit,
            'form': CircuitForm(circuit=circuit)
        }

    def get(self, request, circuit_id):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to='/login')
        return render(request, "manage/edit.html", context=self.generate_data(circuit_id))

    def post(self, request, circuit_id):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to='/login')

        try:
            with transaction.atomic():
                circuit = elections.models.Circuit.objects.select_for_update().filter(id=circuit_id)[0]
                form = CircuitForm(request.POST, circuit=circuit)

                if not form.is_valid():
                    data = self.generate_data(circuit_id)
                    data["form"] = form
                    return render(request, "manage/edit.html", context=data)

                candidates = []
                valid_votes = 0
                for candidate_id, votes in form.cleaned_data.items():
                    c = elections.models.CandidateResult.objects.get(candidate_id=candidate_id, circuit_id=circuit.id)
                    if not c:
                        return HttpResponse("Given candidate not found.")
                    c.votes = votes
                    candidates.append(c)
                    valid_votes += votes

                circuit.valid_cards = valid_votes
                circuit.save()
                for c in candidates:
                    c.save()

                return HttpResponseRedirect('/borough/' + str(circuit.borough_id))

        except IntegrityError:
            return HttpResponseServerError("Integrity error. Please redo your changes.")
