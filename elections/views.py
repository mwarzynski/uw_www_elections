from django.http.response import Http404, HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.views import View
from django.shortcuts import render
from elections.forms import CircuitForm
import elections.models


class MainView(View):
    @staticmethod
    def prepare_people(results):
        s = 0
        for r in results:
            s += r.votes
        for r in results:
            r.percentage = r.votes * 100 / s
        i = 1
        for r in results:
            r.index = i
            i += 1
        return results

    @staticmethod
    def get_circuit(circuit_id):
        try:
            return elections.models.Circuit.objects.get(id=circuit_id)
        except elections.models.CandidateResult.DoesNotExist:
            raise Http404("Given circuit not found.")


class Country(MainView):
    def get(self, request):
        data = {
            'country_mode': True,
            "title": "Wybory prezydenckie 2000"
        }

        results = elections.models.Candidate.objects.annotate(votes=Sum('candidateresult__votes')).order_by('-votes')
        data["people"] = self.prepare_people(results)
        data["voivodeships"] = elections.models.Voivodeship.objects.annotate(votes=Sum('precinct__boroughs__circuit__candidateresult__votes'))

        return render(request, "elections/index.html", context=data)


class Voivodeship(MainView):
    def get(self, request, voivodeship_id):
        v = elections.models.Voivodeship.objects.filter(id=voivodeship_id)
        if not v:
            raise Http404("Voivodeship not found.")
        v = v.first()

        people = elections.models.Candidate.objects.filter(candidateresult__circuit__borough__precinct__voivodeship_id=v.id).annotate(
            votes=Sum('candidateresult__votes')).order_by('-votes')

        data = {
            "title": "Województwo - " + v.name,
            "people": self.prepare_people(people)
        }

        precincts = elections.models.Precinct.objects.filter(voivodeship_id=v.id)
        pages = []
        for p in precincts:
            pages.append({'link': 'precinct/' + str(p.id), 'name': p.name + " (" + str(p.id) + ")"})
        data["pages"] = pages

        return render(request, "elections/index.html", context=data)


class Precinct(MainView):
    def get(self, request, precinct_id):
        precinct = elections.models.Precinct.objects.filter(id=precinct_id)
        if not precinct:
            raise Http404("Precinct not found.")
        precinct = precinct.first()

        people = elections.models.Candidate.objects.filter(candidateresult__circuit__borough__precinct=precinct.id).annotate(
            votes=Sum('candidateresult__votes')).order_by('-votes')

        data = {
            "title": "Okręg - " + precinct.name,
            "people": self.prepare_people(people)
        }

        boroughs = elections.models.Borough.objects.filter(precinct=precinct.id)
        pages = []
        for b in boroughs:
            pages.append({'link': 'borough/' + str(b.id), 'name': b.name})
        data["pages"] = pages

        return render(request, "elections/index.html", context=data)


class Borough(MainView):
    def get(self, request, borough_id):
        borough = elections.models.Borough.objects.filter(id=borough_id)
        if not borough:
            raise Http404("Precinct not found.")
        borough = borough.first()

        people = elections.models.Candidate.objects.filter(candidateresult__circuit__borough=borough.id).annotate(
            votes=Sum('candidateresult__votes')).order_by('-votes')

        data = {
            "borough_mode": True,
            "title": "Gmina - " + borough.name,
            "people": self.prepare_people(people),
            "candidates": elections.models.Candidate.objects.order_by("last_name")
        }

        circuits = []
        i = 1
        for circuit in elections.models.Circuit.objects.filter(borough=borough.id).order_by("id"):
            candidates = elections.models.Candidate.objects.filter(candidateresult__circuit=circuit.id).annotate(votes=Sum('candidateresult__votes')).order_by(
                'last_name')
            circuits.append({
                'i': i,
                'id': circuit.id,
                'address': circuit.address,
                'candidates': candidates
            })
            i += 1
        data['circuits'] = circuits

        return render(request, "elections/index.html", context=data)


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
